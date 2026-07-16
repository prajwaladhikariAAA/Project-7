"""Sales-tax / VAT calculation tool."""

from __future__ import annotations

from accounting_core import Tool

from .calculator import InvoiceTax, LineItem, calculate_tax

__all__ = ["calculate_tax", "LineItem", "InvoiceTax", "get_tool"]

__version__ = "0.1.0"


def get_tool() -> Tool:
    """Registry descriptor discovered via the ``accounting.tools`` entry point."""
    return Tool(
        name="tax_calculator",
        summary="Compute sales tax / VAT for invoice line items.",
        run=calculate_tax,
        version=__version__,
    )
