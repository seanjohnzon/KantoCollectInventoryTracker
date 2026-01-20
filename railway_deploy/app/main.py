"""FastAPI application entrypoint."""

from __future__ import annotations

from typing import Generator

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.db import create_db_and_tables, get_engine, get_session, get_session_factory
from app.schemas import IngestRequest, IngestResponse, ItemCount, ItemReportResponse
from app.services.ingestion import ingest_csv_files
from app.services.reporting import get_item_counts

app = FastAPI(title="KantoCollectInventory")

engine = get_engine()
SessionLocal = get_session_factory(engine)


@app.on_event("startup")
def startup() -> None:
    """
    Initialize database tables on startup.
    """
    create_db_and_tables(engine)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency that yields a SQLAlchemy session.

    Yields:
        Session: SQLAlchemy session.
    """
    yield from get_session(SessionLocal)


@app.post("/ingest", response_model=IngestResponse)
def ingest_csvs(
    request: IngestRequest, session: Session = Depends(get_db_session)
) -> IngestResponse:
    """
    Ingest Whatnot CSV files into the database.

    Args:
        request (IngestRequest): CSV ingestion request.
        session (Session): SQLAlchemy session dependency.

    Returns:
        IngestResponse: Summary of ingestion results.
    """
    result = ingest_csv_files(
        session=session,
        csv_paths=request.csv_paths,
        include_non_sales=request.include_non_sales,
    )
    return IngestResponse(
        files_processed=result.files_processed,
        rows_loaded=result.rows_loaded,
        rows_skipped=result.rows_skipped,
    )


@app.get("/reports/items", response_model=ItemReportResponse)
def report_items(
    group_by_buyer: bool = False,
    include_non_sales: bool = False,
    session: Session = Depends(get_db_session),
) -> ItemReportResponse:
    """
    Get aggregated item counts with optional buyer grouping.

    Args:
        group_by_buyer (bool): Include buyer names in grouping when True.
        include_non_sales (bool): Include giveaways or non-sales when True.
        session (Session): SQLAlchemy session dependency.

    Returns:
        ItemReportResponse: Aggregated report response.
    """
    rows = get_item_counts(
        session=session,
        group_by_buyer=group_by_buyer,
        include_non_sales=include_non_sales,
    )
    results = [ItemCount(**row) for row in rows]
    total_items = sum(item.quantity_sold for item in results)
    return ItemReportResponse(total_items=total_items, results=results)
