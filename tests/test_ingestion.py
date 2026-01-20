"""Tests for CSV ingestion."""

from __future__ import annotations

import csv
from pathlib import Path

from app.db import create_db_and_tables, get_engine, get_session_factory
from app.services.ingestion import ingest_csv_files


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """
    Write rows to a CSV file.

    Args:
        path (Path): Output CSV path.
        rows (list[dict[str, str]]): Rows to write.
    """
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_ingest_sales_only(tmp_path: Path) -> None:
    """
    Ingest only sale rows when include_non_sales is False.
    """
    csv_path = tmp_path / "sales.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "1",
                "LISTING_TITLE": "Pikachu V",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "2",
                "TRANSACTION_AMOUNT": "10.00",
                "BUYER_PAID": "10.00",
                "ORIGINAL_ITEM_PRICE": "10.00",
            },
            {
                "ORDER_ID": "2",
                "LISTING_TITLE": "Giveaway",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "-4.00",
                "BUYER_PAID": "0.00",
                "ORIGINAL_ITEM_PRICE": "0.00",
            },
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        result = ingest_csv_files(session, [str(csv_path)], include_non_sales=False)

    assert result.files_processed == 1
    assert result.rows_loaded == 1
    assert result.rows_skipped == 1


def test_ingest_defaults_quantity(tmp_path: Path) -> None:
    """
    Default quantity to 1 when the CSV value is blank.
    """
    csv_path = tmp_path / "quantity.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "3",
                "LISTING_TITLE": "Charizard",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "",
                "TRANSACTION_AMOUNT": "25.00",
                "BUYER_PAID": "25.00",
                "ORIGINAL_ITEM_PRICE": "25.00",
            }
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        result = ingest_csv_files(session, [str(csv_path)], include_non_sales=False)

    assert result.rows_loaded == 1


def test_ingest_missing_order_id_skips(tmp_path: Path) -> None:
    """
    Skip rows when required fields are missing.
    """
    csv_path = tmp_path / "invalid.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "",
                "LISTING_TITLE": "Bulbasaur",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "5.00",
                "BUYER_PAID": "5.00",
                "ORIGINAL_ITEM_PRICE": "5.00",
            }
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)

    with session_factory() as session:
        result = ingest_csv_files(session, [str(csv_path)], include_non_sales=False)

    assert result.rows_loaded == 0
    assert result.rows_skipped == 1
