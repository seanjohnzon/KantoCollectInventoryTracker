"""Tests for local UI helpers."""

from __future__ import annotations

from typing import Optional

from app.schemas import ItemCount, ItemReportResponse
from app.ui import _coerce_checkbox, _render_report_table


def _build_report(total: int, buyer: Optional[str] = None) -> ItemReportResponse:
    """
    Build a report payload for tests.

    Args:
        total (int): Total item count.
        buyer (Optional[str]): Buyer name.

    Returns:
        ItemReportResponse: Report payload.
    """
    item = ItemCount(listing_title="Test Item", quantity_sold=total, buyer_name=buyer)
    return ItemReportResponse(total_items=total, results=[item])


def test_render_report_table_expected() -> None:
    """
    Render a table with results.
    """
    report = _build_report(2, buyer="ash")
    html = _render_report_table(report)
    assert "<table>" in html
    assert "Test Item" in html
    assert "ash" in html


def test_render_report_table_empty_results() -> None:
    """
    Render a fallback message when there are no results.
    """
    report = ItemReportResponse(total_items=0, results=[])
    html = _render_report_table(report)
    assert "No results found" in html


def test_coerce_checkbox_failure() -> None:
    """
    Treat unknown checkbox values as False.
    """
    assert _coerce_checkbox("maybe") is False
