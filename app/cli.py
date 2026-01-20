"""CLI entrypoint for local ingestion and reporting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from app.db import create_db_and_tables, get_engine, get_session_factory
from app.schemas import IngestResponse, ItemCount, ItemReportResponse
from app.services.ingestion import IngestResult, ingest_csv_files
from app.services.reporting import get_item_counts


def build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured CLI parser.
    """
    parser = argparse.ArgumentParser(description="KantoCollectInventory CLI")
    parser.add_argument(
        "--db-path",
        dest="db_path",
        default=None,
        help="Override SQLite database path (default: data/inventory.db)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest Whatnot CSV files")
    ingest_parser.add_argument("inputs", nargs="+", help="CSV file(s) or directories")
    ingest_parser.add_argument(
        "--include-non-sales",
        action="store_true",
        help="Include giveaways or non-sales",
    )

    report_parser = subparsers.add_parser("report", help="Report item counts")
    report_parser.add_argument(
        "--group-by-buyer",
        action="store_true",
        help="Group counts by buyer name",
    )
    report_parser.add_argument(
        "--title-match",
        choices=["exact", "case_insensitive", "aggressive", "custom"],
        default="exact",
        help="How to match listing titles",
    )
    report_parser.add_argument(
        "--include-non-sales",
        action="store_true",
        help="Include giveaways or non-sales",
    )

    return parser


def _database_url_from_path(db_path: str | None) -> str | None:
    """
    Convert a database path into a SQLite SQLAlchemy URL.

    Args:
        db_path (str | None): Database path or None to use defaults.

    Returns:
        str | None: SQLAlchemy URL or None to use default settings.
    """
    if not db_path:
        return None
    resolved = Path(db_path).expanduser()
    return f"sqlite+pysqlite:///{resolved}"


def _expand_inputs(inputs: Iterable[str]) -> list[str]:
    """
    Expand file and directory inputs into CSV paths.

    Args:
        inputs (Iterable[str]): Input paths.

    Returns:
        list[str]: Expanded CSV file paths.
    """
    expanded: list[str] = []
    for entry in inputs:
        path = Path(entry).expanduser()
        if path.is_dir():
            # Reason: Users pass a folder with multiple Whatnot exports.
            expanded.extend(sorted(str(item) for item in path.glob("*.csv")))
        else:
            expanded.append(str(path))
    return expanded


def run_ingest(
    inputs: Iterable[str], include_non_sales: bool, db_path: str | None = None
) -> IngestResult:
    """
    Ingest CSV files into the database.

    Args:
        inputs (Iterable[str]): CSV file or directory inputs.
        include_non_sales (bool): Include giveaways or non-sales when True.
        db_path (str | None): Optional database path override.

    Returns:
        IngestResult: Summary of ingestion results.
    """
    csv_paths = _expand_inputs(inputs)
    engine = get_engine(_database_url_from_path(db_path))
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        return ingest_csv_files(
            session=session,
            csv_paths=csv_paths,
            include_non_sales=include_non_sales,
        )


def run_report(
    group_by_buyer: bool,
    include_non_sales: bool,
    title_match: str,
    db_path: str | None = None,
) -> ItemReportResponse:
    """
    Generate item count reports.

    Args:
        group_by_buyer (bool): Group counts by buyer name when True.
        include_non_sales (bool): Include giveaways or non-sales when True.
        title_match (str): How to match titles.
        db_path (str | None): Optional database path override.

    Returns:
        ItemReportResponse: Report payload.
    """
    engine = get_engine(_database_url_from_path(db_path))
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        rows = get_item_counts(
            session=session,
            group_by_buyer=group_by_buyer,
            include_non_sales=include_non_sales,
            title_match=title_match,
        )
    results = [ItemCount(**row) for row in rows]
    total_items = sum(item.quantity_sold for item in results)
    return ItemReportResponse(total_items=total_items, results=results)


def main() -> None:
    """
    Run the CLI tool.
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        result = run_ingest(
            inputs=args.inputs,
            include_non_sales=args.include_non_sales,
            db_path=args.db_path,
        )
        response = IngestResponse(
            files_processed=result.files_processed,
            rows_loaded=result.rows_loaded,
            rows_skipped=result.rows_skipped,
        )
        print(json.dumps(response.model_dump(), indent=2))
        return

    report = run_report(
        group_by_buyer=args.group_by_buyer,
        include_non_sales=args.include_non_sales,
        title_match=args.title_match,
        db_path=args.db_path,
    )
    print(json.dumps(report.model_dump(), indent=2))


if __name__ == "__main__":
    main()
