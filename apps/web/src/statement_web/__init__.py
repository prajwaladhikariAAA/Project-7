"""Web app for converting bank-statement PDFs to CSV/JSON."""

from __future__ import annotations

from .app import app, main

__all__ = ["app", "main"]

__version__ = "0.1.0"
