# ledger-reconciler

Matches bank-statement transactions against general-ledger entries and reports
what is matched, missing from the books, or missing from the bank.

```python
from datetime import date
from accounting_core import Money, Transaction
from ledger_reconciler import reconcile

bank = [Transaction(date(2026, 1, 5), "ACME deposit", Money.of("1200.00"), "INV-1001")]
book = [Transaction(date(2026, 1, 5), "Invoice 1001", Money.of("1200.00"), "INV-1001")]

result = reconcile(bank, book)
print(result.is_balanced, len(result.matched))
```

Matching strategy: exact `reference` when present, otherwise `(amount, date)`.
