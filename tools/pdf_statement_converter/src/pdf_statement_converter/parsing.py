"""Pure parsing helpers: turn extracted text/tables into statement rows.

These functions never touch a PDF — they operate on plain strings and lists of
cells. Keeping PDF I/O out of here makes the tricky parsing logic easy to test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from accounting_core import Money

# Date token patterns mapped to the strptime formats to try for each.
_DATE_PATTERNS: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"^\s*(\d{4}-\d{1,2}-\d{1,2})"), ["%Y-%m-%d"]),
    (re.compile(r"^\s*(\d{1,2}/\d{1,2}/\d{4})"), ["%m/%d/%Y", "%d/%m/%Y"]),
    (re.compile(r"^\s*(\d{1,2}/\d{1,2}/\d{2})"), ["%m/%d/%y", "%d/%m/%y"]),
    (
        re.compile(r"^\s*(\d{1,2}[-\s][A-Za-z]{3,9}[-\s]\d{2,4})"),
        ["%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%d-%b-%y"],
    ),
]

# A monetary token, e.g. "1,200.00", "$1,200.00", "(45.00)", "-45.00", "45.00 CR".
_AMOUNT_RE = re.compile(
    r"\(?\s*[-+]?\s*[$£€]?\s*\d[\d,]*\.\d{2}\s*\)?(?:\s*[CD]R)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class StatementRow:
    """One parsed transaction line."""

    date: date
    description: str
    amount: Money
    balance: Money | None = None


def parse_amount(token: str, currency: str = "USD") -> Money:
    """Parse a messy monetary token into signed :class:`Money`."""
    text = token.strip()
    negative = False

    if text.startswith("(") and text.rstrip().endswith(")"):
        negative = True
        text = text.strip()[1:-1]

    upper = text.upper().strip()
    if upper.endswith("CR"):
        text = text[: upper.rfind("CR")]
    elif upper.endswith("DR"):
        negative = True
        text = text[: upper.rfind("DR")]

    text = text.replace(",", "")
    for symbol in ("$", "£", "€"):
        text = text.replace(symbol, "")
    text = text.strip()

    if text.startswith("-"):
        negative = True
        text = text[1:]
    elif text.startswith("+"):
        text = text[1:]

    value = Decimal(text.strip())
    return Money(-value if negative else value, currency)


def _try_parse_date(token: str, formats: list[str], dayfirst: bool) -> date | None:
    ordered = formats
    if dayfirst:
        # Prefer day-first interpretations (e.g. DD/MM before MM/DD).
        ordered = sorted(formats, key=lambda f: 0 if f.startswith("%d") else 1)
    normalized = re.sub(r"\s+", " ", token.strip())
    for fmt in ordered:
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue
    return None


def extract_leading_date(
    line: str,
    *,
    date_formats: list[str] | None = None,
    dayfirst: bool = False,
) -> tuple[date, str] | None:
    """Return ``(date, remainder)`` if ``line`` starts with a recognizable date."""
    for pattern, default_formats in _DATE_PATTERNS:
        match = pattern.match(line)
        if not match:
            continue
        formats = date_formats or default_formats
        parsed = _try_parse_date(match.group(1), formats, dayfirst)
        if parsed is not None:
            return parsed, line[match.end():]
    return None


# Lines that start with these (case-insensitive) are treated as summary/section
# noise rather than transactions when a date is being carried forward.
_SUMMARY_PREFIXES = (
    "total",
    "subtotal",
    "sub total",
    "opening balance",
    "closing balance",
    "balance brought forward",
    "balance carried forward",
    "brought forward",
    "carried forward",
    "statement",
    "page ",
    "continued",
)


def _looks_like_summary(text: str) -> bool:
    low = text.strip().lower()
    return low.startswith(_SUMMARY_PREFIXES)


def _row_from_text(
    txn_date: date, text: str, currency: str
) -> StatementRow | None:
    """Build a row from the text following a date (or a carried-date line)."""
    first = _AMOUNT_RE.search(text)
    if first is None:
        return None
    amounts = _AMOUNT_RE.findall(text)

    description = text[: first.start()].strip()
    try:
        amount = parse_amount(amounts[0], currency)
        balance = parse_amount(amounts[-1], currency) if len(amounts) >= 2 else None
    except InvalidOperation:
        return None

    return StatementRow(txn_date, description, amount, balance)


def parse_line(
    line: str,
    *,
    currency: str = "USD",
    date_formats: list[str] | None = None,
    dayfirst: bool = False,
) -> StatementRow | None:
    """Parse a single statement line into a row, or ``None`` if it is not one."""
    found = extract_leading_date(line, date_formats=date_formats, dayfirst=dayfirst)
    if found is None:
        return None
    txn_date, rest = found
    return _row_from_text(txn_date, rest, currency)


def parse_text(
    lines: list[str],
    *,
    currency: str = "USD",
    date_formats: list[str] | None = None,
    dayfirst: bool = False,
    carry_date: bool = True,
) -> list[StatementRow]:
    """Parse every transaction found in ``lines``.

    Handles two common layouts:

    - **Date per line** — each transaction line starts with its own date.
    - **Grouped by date** — a date appears once and following lines omit it. With
      ``carry_date=True`` (default) the last seen date is applied to subsequent
      transaction lines. Lines that look like summaries/totals are skipped so they
      are not mistaken for transactions. Set ``carry_date=False`` if a per-line-date
      statement over-captures footer/total lines.
    """
    rows: list[StatementRow] = []
    last_date: date | None = None
    for line in lines:
        found = extract_leading_date(
            line, date_formats=date_formats, dayfirst=dayfirst
        )
        if found is not None:
            last_date, rest = found
            row = _row_from_text(last_date, rest, currency)
            if row is not None:
                rows.append(row)
        elif carry_date and last_date is not None and not _looks_like_summary(line):
            row = _row_from_text(last_date, line, currency)
            if row is not None:
                rows.append(row)
    return rows


_HEADER_ALIASES = {
    "date": ("date", "posted", "transaction date"),
    "description": ("description", "details", "particulars", "narration", "memo", "payee"),
    "amount": ("amount", "value"),
    "debit": ("debit", "withdrawal", "paid out", "money out"),
    "credit": ("credit", "deposit", "paid in", "money in"),
    "balance": ("balance",),
}


def _cell(cells: list[str], cols: dict[str, int], field: str) -> str:
    idx = cols.get(field)
    return cells[idx] if idx is not None and idx < len(cells) else ""


def _detect_columns(header: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for index, cell in enumerate(header):
        label = (cell or "").strip().lower()
        for field, aliases in _HEADER_ALIASES.items():
            if field in mapping:
                continue
            if any(alias in label for alias in aliases):
                mapping[field] = index
    return mapping


def parse_tables(
    tables: list[list[list[str | None]]],
    *,
    currency: str = "USD",
    date_formats: list[str] | None = None,
    dayfirst: bool = False,
    carry_date: bool = True,
) -> list[StatementRow]:
    """Parse rows from extracted tables using header detection.

    Supports a single ``amount`` column or separate ``debit``/``credit`` columns
    (amount = credit - debit). With ``carry_date=True`` (default), rows whose date
    cell is blank inherit the previous row's date, handling statements that group
    several transactions under one date.
    """
    rows: list[StatementRow] = []
    for table in tables:
        if not table:
            continue
        cols = _detect_columns([c or "" for c in table[0]])
        if "date" not in cols or (
            "amount" not in cols and "debit" not in cols and "credit" not in cols
        ):
            continue

        last_date: date | None = None
        for raw in table[1:]:
            cells = [(c or "").strip() for c in raw]

            found = extract_leading_date(
                _cell(cells, cols, "date"), date_formats=date_formats, dayfirst=dayfirst
            )
            if found is not None:
                last_date = found[0]
            elif not (carry_date and last_date is not None):
                continue
            txn_date = last_date
            assert txn_date is not None

            amount_cell = _cell(cells, cols, "amount")
            debit_cell = _cell(cells, cols, "debit")
            credit_cell = _cell(cells, cols, "credit")
            if not (amount_cell or debit_cell or credit_cell):
                continue  # blank / continuation row with no movement

            zero = Money.of("0", currency)
            try:
                if "amount" in cols and amount_cell:
                    amount = parse_amount(amount_cell, currency)
                else:
                    debit = parse_amount(debit_cell, currency) if debit_cell else zero
                    credit = parse_amount(credit_cell, currency) if credit_cell else zero
                    amount = credit - debit
                balance_cell = _cell(cells, cols, "balance")
                balance = parse_amount(balance_cell, currency) if balance_cell else None
            except (InvalidOperation, ValueError):
                continue

            description = _cell(cells, cols, "description")
            rows.append(StatementRow(txn_date, description, amount, balance))
    return rows
