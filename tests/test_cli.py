"""Tests for CLI helpers."""

from __future__ import annotations

import csv
from pathlib import Path

from app.cli import _expand_inputs, run_ingest, run_report


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


def test_expand_inputs_directory(tmp_path: Path) -> None:
    """
    Expand a directory into sorted CSV paths.
    """
    csv_a = tmp_path / "a.csv"
    csv_b = tmp_path / "b.csv"
    _write_csv(
        csv_a,
        [
            {
                "ORDER_ID": "1",
                "LISTING_TITLE": "Item A",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "1.00",
                "BUYER_PAID": "1.00",
                "ORIGINAL_ITEM_PRICE": "1.00",
            }
        ],
    )
    _write_csv(
        csv_b,
        [
            {
                "ORDER_ID": "2",
                "LISTING_TITLE": "Item B",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "1.00",
                "BUYER_PAID": "1.00",
                "ORIGINAL_ITEM_PRICE": "1.00",
            }
        ],
    )

    expanded = _expand_inputs([str(tmp_path)])
    assert expanded == [str(csv_a), str(csv_b)]


def test_run_ingest_and_report(tmp_path: Path) -> None:
    """
    Ingest CSV rows and produce a grouped report.
    """
    csv_path = tmp_path / "sales.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "10",
                "LISTING_TITLE": "Promo Pack",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "2",
                "TRANSACTION_AMOUNT": "6.00",
                "BUYER_PAID": "6.00",
                "ORIGINAL_ITEM_PRICE": "6.00",
                "BUYER_NAME": "brock",
            }
        ],
    )
    db_path = tmp_path / "inventory.db"

    ingest_result = run_ingest([str(csv_path)], include_non_sales=False, db_path=str(db_path))
    assert ingest_result.rows_loaded == 1

    report = run_report(
        group_by_buyer=True,
        include_non_sales=False,
        title_match="exact",
        db_path=str(db_path),
    )
    assert report.total_items == 2
    assert report.results[0].buyer_name == "brock"
