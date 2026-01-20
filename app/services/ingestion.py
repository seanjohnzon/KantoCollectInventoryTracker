"""CSV ingestion service."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.schemas import CsvRow


@dataclass(frozen=True)
class IngestResult:
    """Result counts from a CSV ingestion run."""

    files_processed: int
    rows_loaded: int
    rows_skipped: int


def is_sale_row(row: CsvRow) -> bool:
    """
    Determine if a CSV row represents a sold item.

    Args:
        row (CsvRow): Parsed CSV row.

    Returns:
        bool: True when the row represents a sale.
    """
    if row.transaction_type != "ORDER_EARNINGS":
        return False
    if row.transaction_amount > 0:
        return True
    if row.buyer_paid > 0:
        return True
    return row.original_item_price > 0


def _extract_quantity_multiplier(title: str) -> int:
    """
    Extract quantity multiplier from title (e.g., "2x Pack", "5x", "Packs x 3").
    
    Rules:
    - "2x Pack", "5x Pack" → multiplier = 2, 5
    - "3 Pack Blister", "3-Pack Blister" → NOT a multiplier (product name)
    - "#4", "#11" → NOT a multiplier (shipping identifier)
    - Default → 1

    Args:
        title (str): Raw listing title.

    Returns:
        int: Quantity multiplier (1 if none found).
    """
    import re
    lowered = title.lower()
    
    # Skip product names with "blister" - these are product types, not multipliers
    # e.g., "3 Pack Blister - Phantasmal Flames" is ONE product, not 3x
    if 'blister' in lowered and re.search(r'\b\d+\s*-?\s*pack\s+blister\b', lowered):
        return 1
    
    # Match patterns like "2x pack", "5x pack"
    match = re.search(r'\b(\d+)x\s*pack\b', lowered)
    if match:
        return int(match.group(1))
    
    # Match patterns like "2x", "5x" (standalone, not followed by "pack" in blister context)
    match = re.search(r'\b(\d+)x\b', lowered)
    if match and 'blister' not in lowered:
        return int(match.group(1))
    
    # Match patterns like "packs x 5", "pack x 3"
    match = re.search(r'\bpacks?\s*x\s*(\d+)\b', lowered)
    if match:
        return int(match.group(1))
    
    return 1


def _normalize_title(title: str) -> str:
    """
    Normalize listing titles for consistent grouping.

    Args:
        title (str): Raw listing title.

    Returns:
        str: Normalized title.
    """
    return " ".join(title.strip().split())


def ingest_csv_files(
    session: Session, csv_paths: Iterable[str], include_non_sales: bool = False
) -> IngestResult:
    """
    Ingest Whatnot CSV files into the database.

    Args:
        session (Session): SQLAlchemy session.
        csv_paths (Iterable[str]): Paths to CSV files.
        include_non_sales (bool): Whether to include giveaways or non-sales.

    Returns:
        IngestResult: Summary of the ingestion.

    Raises:
        FileNotFoundError: When a CSV path does not exist.
    """
    files_processed = 0
    rows_loaded = 0
    rows_skipped = 0

    for csv_path in csv_paths:
        path = Path(csv_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for raw_row in reader:
                try:
                    row = CsvRow.model_validate(raw_row)
                except ValidationError:
                    rows_skipped += 1
                    continue

                if not row.order_id or not row.listing_title:
                    rows_skipped += 1
                    continue
                sale_flag = is_sale_row(row)
                if not include_non_sales and not sale_flag:
                    rows_skipped += 1
                    continue

                existing = session.execute(
                    select(Transaction).where(Transaction.order_id == row.order_id)
                ).scalar_one_or_none()
                if existing:
                    rows_skipped += 1
                    continue

                # Extract quantity multiplier from title
                multiplier = _extract_quantity_multiplier(row.listing_title)
                actual_quantity = row.quantity_sold * multiplier

                transaction = Transaction(
                    order_id=row.order_id,
                    listing_title=_normalize_title(row.listing_title),
                    listing_description=row.listing_description,
                    product_category=row.product_category,
                    buy_format=row.buy_format,
                    sale_type=row.sale_type,
                    quantity_sold=actual_quantity,
                    transaction_amount=row.transaction_amount,
                    buyer_paid=row.buyer_paid,
                    original_item_price=row.original_item_price,
                    transaction_type=row.transaction_type,
                    buyer_name=row.buyer_name,
                    buyer_state=row.buyer_state,
                    buyer_country=row.buyer_country,
                    order_placed_at=row.order_placed_at_utc,
                    transaction_completed_at=row.transaction_completed_at_utc,
                    source_file=str(path),
                    is_sale=sale_flag,
                )
                session.add(transaction)
                rows_loaded += 1
        files_processed += 1

    session.commit()
    return IngestResult(
        files_processed=files_processed,
        rows_loaded=rows_loaded,
        rows_skipped=rows_skipped,
    )
