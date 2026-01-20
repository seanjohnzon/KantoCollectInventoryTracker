## KantoCollectInventory

Local CLI tool and web UI that ingest Whatnot CSV exports into a SQLite database, 
return sold-item counts, and manage inventory allocation with owner assignment and pricing.

### Setup
1. Create a virtual environment and install dependencies:
   - `pip install -r requirements.txt`

### Local Web UI
Start the local UI:
```
python3 -m app.ui
```
Open `http://127.0.0.1:5173` in your browser.

**Features:**
- **Overview**: Total inventory stats and allocation summary by owner
- **Owner Views**: Navigate between Cihan, Askar, Nima, and Kanto to see their allocated items with costs
- **Unallocated**: View remaining items not assigned to any owner, grouped by set

### Ingest CSVs
Example using the provided Whatnot exports:
```
python3 -m app.cli ingest \
  "/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Inventory"
```

### Report Counts
```
python3 -m app.cli report --group-by-buyer
```
Optional title matching:
- `--title-match exact` (default)
- `--title-match case_insensitive` (merge case/spacing differences)
- `--title-match aggressive` (also strips emojis/punctuation)
- `--title-match custom` (adds rules for giveaways + numbered packs)

### Import Allocations from Excel
Import owner allocations with pricing from an Excel file:
```python
from app.db import get_engine, get_session_factory
from app.services.allocation import import_allocations_from_excel

engine = get_engine("sqlite+pysqlite:///data/inventory.db")
session_factory = get_session_factory(engine)

with session_factory() as session:
    result = import_allocations_from_excel(
        session=session,
        excel_path='path/to/allocations.xlsx',
        title_match='custom',
        dry_run=False
    )
```

Expected Excel format:
- Multiple sheets (one per owner: Cihan, Askar, Nima, Kanto, etc.)
- Columns: `Item Name`, `Cost`, `Count`, `Total Cost`
- The system fuzzy-matches Excel item names to inventory items

### Notes
- The SQLite database is stored at `data/inventory.db` by default.
- Use `--db-path` to override the database location.
- Quantity multipliers (e.g., "2x Pack", "5x Pack") are automatically detected and applied during ingestion.
