"""Reconcile two sets of transactions (e.g. bank statement vs. general ledger)."""

from __future__ import annotations

from dataclasses import dataclass, field

from accounting_core import Money, Transaction


def _match_key(txn: Transaction) -> tuple:
    """Prefer an explicit reference; fall back to (amount, date)."""
    if txn.reference:
        return ("ref", txn.reference)
    return ("amt", txn.amount.currency, str(txn.amount.amount), txn.date)


@dataclass
class ReconciliationResult:
    """Outcome of reconciling bank transactions against ledger entries."""

    matched: list[tuple[Transaction, Transaction]] = field(default_factory=list)
    unmatched_bank: list[Transaction] = field(default_factory=list)
    unmatched_book: list[Transaction] = field(default_factory=list)

    @property
    def is_balanced(self) -> bool:
        return not self.unmatched_bank and not self.unmatched_book

    def unmatched_bank_total(self, currency: str = "USD") -> Money:
        return _sum(self.unmatched_bank, currency)

    def unmatched_book_total(self, currency: str = "USD") -> Money:
        return _sum(self.unmatched_book, currency)


def _sum(txns: list[Transaction], currency: str) -> Money:
    total = Money.of("0", currency)
    for txn in txns:
        total = total + txn.amount
    return total


def reconcile(
    bank: list[Transaction],
    book: list[Transaction],
) -> ReconciliationResult:
    """Match ``bank`` transactions to ``book`` entries.

    Each book entry is used at most once. Matching prefers an exact shared
    ``reference`` and otherwise falls back to identical ``(amount, date)``.
    """
    remaining: dict[tuple, list[Transaction]] = {}
    for entry in book:
        remaining.setdefault(_match_key(entry), []).append(entry)

    result = ReconciliationResult()
    for txn in bank:
        candidates = remaining.get(_match_key(txn))
        if candidates:
            result.matched.append((txn, candidates.pop(0)))
        else:
            result.unmatched_bank.append(txn)

    for leftovers in remaining.values():
        result.unmatched_book.extend(leftovers)

    return result
