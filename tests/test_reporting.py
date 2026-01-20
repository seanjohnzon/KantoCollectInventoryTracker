"""Tests for reporting queries."""

from __future__ import annotations

import csv
from pathlib import Path

from app.db import create_db_and_tables, get_engine, get_session_factory
from app.services.ingestion import ingest_csv_files
from app.services.reporting import get_item_counts


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


def test_report_group_by_buyer(tmp_path: Path) -> None:
    """
    Group results by buyer when requested.
    """
    csv_path = tmp_path / "report.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "1",
                "LISTING_TITLE": "Starter Pack",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "10.00",
                "BUYER_PAID": "10.00",
                "ORIGINAL_ITEM_PRICE": "10.00",
                "BUYER_NAME": "ash",
            },
            {
                "ORDER_ID": "2",
                "LISTING_TITLE": "Starter Pack",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "2",
                "TRANSACTION_AMOUNT": "20.00",
                "BUYER_PAID": "20.00",
                "ORIGINAL_ITEM_PRICE": "20.00",
                "BUYER_NAME": "misty",
            },
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)

    with session_factory() as session:
        ingest_csv_files(session, [str(csv_path)], include_non_sales=False)

    with session_factory() as session:
        results = get_item_counts(session, group_by_buyer=True, include_non_sales=False)

    assert len(results) == 2
    buyers = {result["buyer_name"] for result in results}
    assert buyers == {"ash", "misty"}


def test_report_case_insensitive_titles(tmp_path: Path) -> None:
    """
    Merge items that differ only by case and spacing when requested.
    """
    csv_path = tmp_path / "case.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "1",
                "LISTING_TITLE": "Phantasmal Flames Pack #1",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "5.00",
                "BUYER_PAID": "5.00",
                "ORIGINAL_ITEM_PRICE": "5.00",
            },
            {
                "ORDER_ID": "2",
                "LISTING_TITLE": "  phantasmal  flames pack #1  ",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "2",
                "TRANSACTION_AMOUNT": "10.00",
                "BUYER_PAID": "10.00",
                "ORIGINAL_ITEM_PRICE": "10.00",
            },
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)

    with session_factory() as session:
        ingest_csv_files(session, [str(csv_path)], include_non_sales=False)

    with session_factory() as session:
        results = get_item_counts(
            session,
            group_by_buyer=False,
            include_non_sales=False,
            title_match="case_insensitive",
        )

    assert len(results) == 1
    assert results[0]["quantity_sold"] == 3


def test_report_custom_rules(tmp_path: Path) -> None:
    """
    Apply custom normalization for giveaways and numbered packs.
    """
    csv_path = tmp_path / "custom.csv"
    _write_csv(
        csv_path,
        [
            {
                "ORDER_ID": "1",
                "LISTING_TITLE": "Givyyyyy",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "0.00",
                "BUYER_PAID": "0.00",
                "ORIGINAL_ITEM_PRICE": "0.00",
            },
            {
                "ORDER_ID": "2",
                "LISTING_TITLE": "Free.99 - Random Pokemon Pack #2",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "0.00",
                "BUYER_PAID": "0.00",
                "ORIGINAL_ITEM_PRICE": "0.00",
            },
            {
                "ORDER_ID": "3",
                "LISTING_TITLE": "1X Pack - Phantasmal Flames #10",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "10.00",
                "BUYER_PAID": "10.00",
                "ORIGINAL_ITEM_PRICE": "10.00",
            },
            {
                "ORDER_ID": "4",
                "LISTING_TITLE": "1x Pack - Phantasmal Flames #11",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "2",
                "TRANSACTION_AMOUNT": "20.00",
                "BUYER_PAID": "20.00",
                "ORIGINAL_ITEM_PRICE": "20.00",
            },
            {
                "ORDER_ID": "5",
                "LISTING_TITLE": "Friday Fiesta - Random Pokemon Pack!",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "0.00",
                "BUYER_PAID": "0.00",
                "ORIGINAL_ITEM_PRICE": "0.00",
            },
            {
                "ORDER_ID": "6",
                "LISTING_TITLE": "Phantasmal Flames Sleeved Booster Pack",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "5.00",
                "BUYER_PAID": "5.00",
                "ORIGINAL_ITEM_PRICE": "5.00",
            },
            {
                "ORDER_ID": "7",
                "LISTING_TITLE": "Phantasmal Flames Single Pack Blister",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "6.00",
                "BUYER_PAID": "6.00",
                "ORIGINAL_ITEM_PRICE": "6.00",
            },
            {
                "ORDER_ID": "8",
                "LISTING_TITLE": "Kanto Christmas Gifts - Asian Pokemon Pack",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "0.00",
                "BUYER_PAID": "0.00",
                "ORIGINAL_ITEM_PRICE": "0.00",
            },
            {
                "ORDER_ID": "9",
                "LISTING_TITLE": "Friday Fiesta - 🌀🧿🐉🔥 Elite Trainer Box - Fantasmal Flames 🌀🧿🐉🔥",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "50.00",
                "BUYER_PAID": "50.00",
                "ORIGINAL_ITEM_PRICE": "50.00",
            },
            {
                "ORDER_ID": "10",
                "LISTING_TITLE": "Prismatic Evolutions Booster Bundle",
                "TRANSACTION_TYPE": "ORDER_EARNINGS",
                "QUANTITY_SOLD": "1",
                "TRANSACTION_AMOUNT": "30.00",
                "BUYER_PAID": "30.00",
                "ORIGINAL_ITEM_PRICE": "30.00",
            },
        ],
    )

    engine = get_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    create_db_and_tables(engine)
    session_factory = get_session_factory(engine)

    with session_factory() as session:
        ingest_csv_files(session, [str(csv_path)], include_non_sales=True)

    with session_factory() as session:
        results = get_item_counts(
            session,
            group_by_buyer=False,
            include_non_sales=True,
            title_match="custom",
        )

    titles = {item["listing_title"] for item in results}
    assert "Random Asian Pack" in titles
    assert "Phantasmal Flames Sleeve" in titles
    assert "Phantasmal Flames Blister" in titles
    assert "Fantasmal Flames ETB" in titles
    assert "Prismatic Evolutions Booster Bundle" in titles
    
    # Verify giveaways are grouped (4 giveaway items should be combined)
    giveaway_item = next((item for item in results if item["listing_title"] == "Random Asian Pack"), None)
    assert giveaway_item is not None
    assert giveaway_item["quantity_sold"] == 4  # Orders 1,2,5,8
    
    # Verify Phantasmal Flames Sleeves are grouped (3 single packs)
    sleeve_item = next((item for item in results if item["listing_title"] == "Phantasmal Flames Sleeve"), None)
    assert sleeve_item is not None
    assert sleeve_item["quantity_sold"] == 4  # 1+2+1 from orders 3,4,6
