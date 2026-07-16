"""A ``Decimal``-backed money type.

Accounting math must never use binary floats, which cannot represent values like
``0.10`` exactly. ``Money`` normalises every amount to two decimal places using
banker-safe rounding and refuses to mix currencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Union

Numeric = Union["Money", int, str, Decimal]

_CENTS = Decimal("0.01")


@dataclass(frozen=True, order=True)
class Money:
    """An immutable monetary amount in a single currency."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        quantized = Decimal(self.amount).quantize(_CENTS, rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized)
        object.__setattr__(self, "currency", self.currency.upper())

    @classmethod
    def of(cls, amount: str | int | float | Decimal, currency: str = "USD") -> Money:
        """Build ``Money`` from any numeric-like value (floats via ``str``)."""
        return cls(Decimal(str(amount)), currency)

    def _check(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot combine {self.currency} and {other.currency} amounts"
            )

    def __add__(self, other: Money) -> Money:
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal | str) -> Money:
        return Money(self.amount * Decimal(str(factor)), self.currency)

    __rmul__ = __mul__

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
