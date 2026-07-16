"""Shared foundation for accounting tools: money, models, and the tool registry."""

from __future__ import annotations

from .models import Transaction
from .money import Money
from .registry import Tool, ToolRegistry, load_installed_tools, registry

__all__ = [
    "Money",
    "Transaction",
    "Tool",
    "ToolRegistry",
    "registry",
    "load_installed_tools",
]

__version__ = "0.1.0"
