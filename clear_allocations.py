"""
Script to clear all allocations and reset inventory to unallocated state.
"""
from pathlib import Path
from sqlalchemy import delete
from app.db import get_engine, get_session_factory
from app.models import Allocation


def clear_all_allocations():
    """Delete all allocation records from the database."""
    db_path = Path("data/inventory.db")
    engine = get_engine(f"sqlite+pysqlite:///{db_path}")
    session_factory = get_session_factory(engine)
    
    with session_factory() as session:
        # Count existing allocations
        result = session.execute(delete(Allocation))
        deleted_count = result.rowcount
        session.commit()
        
        print(f"✅ Cleared {deleted_count} allocation records")
        print("All items are now unallocated and ready for manual assignment")


if __name__ == "__main__":
    print("🔄 Clearing all allocations...")
    clear_all_allocations()
