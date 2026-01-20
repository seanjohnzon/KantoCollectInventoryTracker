"""Pydantic models for requests, responses, and CSV validation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CsvRow(BaseModel):
    """Validated subset of a Whatnot CSV row."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="ORDER_ID")
    listing_title: str = Field(alias="LISTING_TITLE")
    listing_description: Optional[str] = Field(default=None, alias="LISTING_DESCRIPTION")
    product_category: Optional[str] = Field(default=None, alias="PRODUCT_CATEGORY")
    buy_format: Optional[str] = Field(default=None, alias="BUY_FORMAT")
    sale_type: Optional[str] = Field(default=None, alias="SALE_TYPE")
    quantity_sold: int = Field(default=1, alias="QUANTITY_SOLD")
    transaction_type: str = Field(alias="TRANSACTION_TYPE")
    transaction_amount: Decimal = Field(default=Decimal("0.00"), alias="TRANSACTION_AMOUNT")
    buyer_paid: Decimal = Field(default=Decimal("0.00"), alias="BUYER_PAID")
    original_item_price: Decimal = Field(default=Decimal("0.00"), alias="ORIGINAL_ITEM_PRICE")
    buyer_name: Optional[str] = Field(default=None, alias="BUYER_NAME")
    buyer_state: Optional[str] = Field(default=None, alias="BUYER_STATE")
    buyer_country: Optional[str] = Field(default=None, alias="BUYER_COUNTRY")
    order_placed_at_utc: Optional[datetime] = Field(
        default=None, alias="ORDER_PLACED_AT_UTC"
    )
    transaction_completed_at_utc: Optional[datetime] = Field(
        default=None, alias="TRANSACTION_COMPLETED_AT_UTC"
    )

    @field_validator(
        "listing_title",
        "listing_description",
        "product_category",
        "buy_format",
        "sale_type",
        "buyer_name",
        "buyer_state",
        "buyer_country",
        mode="before",
    )
    @classmethod
    def _empty_string_to_none(cls, value: Optional[str]) -> Optional[str]:
        """
        Normalize empty strings to None for optional text fields.

        Args:
            value (str | None): Incoming value.

        Returns:
            str | None: Normalized value.
        """
        if value is None:
            return None
        value = value.strip()
        return value if value else None

    @field_validator("quantity_sold", mode="before")
    @classmethod
    def _parse_quantity(cls, value: Union[str, int, None]) -> int:
        """
        Ensure quantity defaults to 1 when missing or blank.

        Args:
            value (str | int | None): Incoming quantity value.

        Returns:
            int: Parsed quantity.
        """
        if value is None:
            return 1
        if isinstance(value, int):
            return value
        value = value.strip()
        return int(value) if value else 1

    @field_validator("transaction_amount", "buyer_paid", "original_item_price", mode="before")
    @classmethod
    def _parse_decimal(cls, value: Union[str, Decimal, None]) -> Decimal:
        """
        Parse decimal values, defaulting to zero for blanks.

        Args:
            value (str | Decimal | None): Incoming value.

        Returns:
            Decimal: Parsed decimal.
        """
        if value is None:
            return Decimal("0.00")
        if isinstance(value, Decimal):
            return value
        value = value.strip()
        return Decimal(value) if value else Decimal("0.00")

    @field_validator("order_placed_at_utc", "transaction_completed_at_utc", mode="before")
    @classmethod
    def _parse_datetime(cls, value: Union[str, datetime, None]) -> Optional[datetime]:
        """
        Normalize blank datetime strings to None.

        Args:
            value (str | datetime | None): Incoming datetime value.

        Returns:
            Optional[datetime]: Parsed datetime or None.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        value = value.strip()
        return value or None


class IngestRequest(BaseModel):
    """API request body for CSV ingestion."""

    csv_paths: List[str]
    include_non_sales: bool = False


class IngestResponse(BaseModel):
    """API response payload for CSV ingestion."""

    files_processed: int
    rows_loaded: int
    rows_skipped: int


class ItemCount(BaseModel):
    """Aggregated count for a listing title (optionally by buyer)."""

    listing_title: str
    quantity_sold: int
    buyer_name: Optional[str] = None


class ItemReportResponse(BaseModel):
    """Report response for item counts."""

    total_items: int
    results: List[ItemCount]
