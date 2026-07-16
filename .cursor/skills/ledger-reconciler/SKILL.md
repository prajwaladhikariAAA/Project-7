---
name: ledger-reconciler
description: Use and extend the ledger-reconciler tool, which matches bank-statement transactions against general-ledger entries. Use when reconciling accounts, matching bank vs. book transactions, or working in tools/ledger_reconciler.
---

# Ledger Reconciler

Located at `tools/ledger_reconciler/`. Matches bank transactions to ledger
entries and reports what is matched vs. unmatched on each side.

## Usage

```python
from datetime import date
from accounting_core import Money, Transaction
from ledger_reconciler import reconcile

bank = [Transaction(date(2026, 1, 5), "ACME deposit", Money.of("1200.00"), "INV-1001")]
book = [Transaction(date(2026, 1, 5), "Invoice 1001", Money.of("1200.00"), "INV-1001")]

result = reconcile(bank, book)
result.is_balanced            # True when nothing is unmatched
result.matched                # list[(bank_txn, book_txn)]
result.unmatched_bank         # in bank, missing from books
result.unmatched_book         # in books, missing from bank
result.unmatched_bank_total() # Money
```

## Matching rules

- Exact shared `reference` when present, else identical `(amount, date)`.
- Each book entry is consumed at most once.

## Extending

Keep the public `reconcile()` signature stable. New matching strategies belong in
`reconciler.py` behind `_match_key`. Add tests in `tools/ledger_reconciler/tests/`
and update this skill when behaviour changes.
