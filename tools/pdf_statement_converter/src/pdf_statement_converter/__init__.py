"""Convert a bank-statement PDF into a CSV of transactions, fully offline."""

from __future__ import annotations

from accounting_core import Tool

from .converter import ConversionResult, convert, to_csv
from .parsing import StatementRow, parse_tables, parse_text
from .verification import BalanceCheck, BalanceDiscrepancy, verify_balances

__all__ = [
    "convert",
    "to_csv",
    "ConversionResult",
    "StatementRow",
    "parse_text",
    "parse_tables",
    "verify_balances",
    "BalanceCheck",
    "BalanceDiscrepancy",
    "get_tool",
]

__version__ = "0.1.0"


def get_tool() -> Tool:
    """Registry descriptor discovered via the ``accounting.tools`` entry point."""
    return Tool(
        name="pdf_statement_converter",
        summary="Convert a bank statement PDF into a CSV of transactions (offline).",
        run=convert,
        version=__version__,
    )
