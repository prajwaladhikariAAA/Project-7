"""Running-balance verification — the accuracy safeguard for parsed statements.

For a correctly parsed statement, each row's running balance must equal the
previous balance plus that row's signed amount. Checking this across the whole
statement catches wrong signs, mis-parsed amounts, and missed/duplicated rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from accounting_core import Money

from .parsing import StatementRow


@dataclass(frozen=True)
class BalanceDiscrepancy:
    """A single row whose running balance did not reconcile."""

    index: int
    date: date
    description: str
    amount: Money
    expected_balance: Money
    actual_balance: Money

    @property
    def difference(self) -> Money:
        return self.actual_balance - self.expected_balance


@dataclass
class BalanceCheck:
    """Result of verifying a statement's running balance."""

    checked: int = 0
    discrepancies: list[BalanceDiscrepancy] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.discrepancies


def verify_balances(
    rows: list[StatementRow],
    *,
    opening_balance: Money | None = None,
) -> BalanceCheck:
    """Verify that running balances reconcile with amounts.

    Walks the rows maintaining an expected balance. Whenever a row carries an
    actual balance, it is compared against the expected value. If
    ``opening_balance`` is given, the very first row is verified too; otherwise the
    first row with a balance seeds the running total. After a mismatch the expected
    value resynchronises to the row's actual balance so a single bad row does not
    cascade into every later row.
    """
    check = BalanceCheck()
    running: Money | None = opening_balance

    for index, row in enumerate(rows):
        if running is not None:
            running = running + row.amount

        if row.balance is None:
            continue

        if running is None:
            running = row.balance
            continue

        check.checked += 1
        if running != row.balance:
            check.discrepancies.append(
                BalanceDiscrepancy(
                    index=index,
                    date=row.date,
                    description=row.description,
                    amount=row.amount,
                    expected_balance=running,
                    actual_balance=row.balance,
                )
            )
            running = row.balance  # resync to avoid cascading errors

    return check
