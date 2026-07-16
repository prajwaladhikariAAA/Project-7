"""Ledger reconciliation tool."""

from __future__ import annotations

from accounting_core import Tool

from .reconciler import ReconciliationResult, reconcile

__all__ = ["reconcile", "ReconciliationResult", "get_tool"]

__version__ = "0.1.0"


def get_tool() -> Tool:
    """Registry descriptor discovered via the ``accounting.tools`` entry point."""
    return Tool(
        name="ledger_reconciler",
        summary="Reconcile bank transactions against general-ledger entries.",
        run=reconcile,
        version=__version__,
    )
