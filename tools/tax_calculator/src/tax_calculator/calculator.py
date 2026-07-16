"""Compute sales tax / VAT for one or more invoice line items."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from accounting_core import Money


@dataclass(frozen=True)
class LineItem:
    """A billable line: a net amount taxed at ``rate`` (a fraction, 0.20 == 20%)."""

    description: str
    net: str | int | float | Decimal
    rate: str | int | float | Decimal = "0"
    currency: str = "USD"

    def as_money(self) -> Money:
        return Money.of(self.net, self.currency)


@dataclass(frozen=True)
class InvoiceTax:
    """Totals for a taxed invoice."""

    net: Money
    tax: Money
    gross: Money


def calculate_tax(items: list[LineItem], currency: str = "USD") -> InvoiceTax:
    """Sum the net, tax, and gross across ``items``.

    Tax is computed and rounded per line item (the norm for invoices) before the
    totals are summed, so each line's rounding is independent.
    """
    net_total = Money.of("0", currency)
    tax_total = Money.of("0", currency)

    for item in items:
        line_net = item.as_money()
        line_tax = line_net * Decimal(str(item.rate))
        net_total = net_total + line_net
        tax_total = tax_total + line_tax

    return InvoiceTax(net=net_total, tax=tax_total, gross=net_total + tax_total)
