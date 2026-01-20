"""Database models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Transaction(Base):
    """Represents a Whatnot transaction line item."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    listing_title: Mapped[str] = mapped_column(String, index=True)
    listing_description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    product_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    buy_format: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sale_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    quantity_sold: Mapped[int] = mapped_column(Integer, default=1)
    transaction_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    buyer_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    original_item_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    transaction_type: Mapped[str] = mapped_column(String)
    buyer_name: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    buyer_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    buyer_country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    order_placed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    transaction_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source_file: Mapped[str] = mapped_column(String)
    is_sale: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Allocation(Base):
    """Represents inventory allocation to owners with pricing."""

    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    normalized_item_name: Mapped[str] = mapped_column(String, index=True)
    owner: Mapped[str] = mapped_column(String, index=True)
    allocated_quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    excel_item_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ProductImage(Base):
    """Represents product images for UI display."""

    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    normalized_item_name: Mapped[str] = mapped_column(String, unique=True, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
