"""Domain models shared across tools."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .money import Money


@dataclass(frozen=True)
class Transaction:
    """A single accounting transaction exchanged between tools.

    ``amount`` is signed: positive for money in (debits to cash), negative for
    money out. ``reference`` is an optional identifier (invoice no., cheque no.)
    that tools such as the reconciler can use for exact matching.
    """

    date: date
    description: str
    amount: Money
    reference: str | None = None
