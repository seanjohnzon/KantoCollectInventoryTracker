## Project Overview
Build a local CLI and web UI that ingest Whatnot CSV exports into a SQLite
database, print item count reports, and manage inventory allocation with owner
assignment and pricing. The FastAPI API can be added later when you're ready to deploy.

## Architecture
- `app/cli.py`: CLI entrypoint for ingestion and reporting.
- `app/ui.py`: Local web UI (runs on localhost) with owner navigation.
- `app/main.py`: Optional FastAPI app and API endpoints (for later).
- `app/db.py`: database configuration and session helpers.
- `app/models.py`: SQLAlchemy ORM models (Transaction, Allocation).
- `app/schemas.py`: Pydantic request/response models and CSV row validation.
- `app/services/ingestion.py`: CSV parsing and database ingestion logic.
- `app/services/reporting.py`: reporting queries for counts and summaries.
- `app/services/allocation.py`: allocation management and Excel import.
- `tests/`: pytest unit tests mirroring `app/` structure.

## Data Flow
1. CSV files are parsed with `csv.DictReader`.
2. Each row is validated with a Pydantic model.
3. Rows are inserted into SQLite with deduping on `order_id`.
4. Reports aggregate `quantity_sold` by listing title and optional buyer.
5. Allocations are imported from Excel with fuzzy matching to inventory items.
6. UI displays allocations by owner with pricing and shows unallocated items.

## Key Features
- **Title Normalization**: Multiple modes (exact, case_insensitive, aggressive, custom)
  to handle seller naming inconsistencies.
- **Quantity Multipliers**: Automatically detects "2x Pack", "5x Pack" patterns and
  multiplies quantity accordingly.
- **Set-Based Categorization**: Groups items by set for easier review and navigation.
- **Allocation System**: Import owner assignments from Excel with unit costs.
- **Fuzzy Matching**: Automatically matches Excel item names to inventory items.

## Conventions
- Python only, PEP8, type hints, `black` formatting.
- Use Pydantic for validation.
- Keep files under 500 LOC; split by responsibility.
