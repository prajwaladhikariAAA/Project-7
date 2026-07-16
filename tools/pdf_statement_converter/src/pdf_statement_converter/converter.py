"""PDF -> CSV conversion. This is the only module that touches a PDF file."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from .parsing import StatementRow, parse_tables, parse_text

CSV_HEADER = ["date", "description", "amount", "balance", "currency"]


@dataclass(frozen=True)
class ConversionResult:
    """Outcome of a conversion: the parsed rows plus the generated CSV."""

    rows: list[StatementRow]
    csv_text: str
    csv_path: Path | None = None


def to_csv(rows: list[StatementRow]) -> str:
    """Render statement rows as CSV text."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for row in rows:
        writer.writerow([
            row.date.isoformat(),
            row.description,
            str(row.amount.amount),
            "" if row.balance is None else str(row.balance.amount),
            row.amount.currency,
        ])
    return buffer.getvalue()


def convert(
    pdf_path: str | Path,
    csv_path: str | Path | None = None,
    *,
    strategy: str = "auto",
    currency: str = "USD",
    date_formats: list[str] | None = None,
    dayfirst: bool = False,
    pages: list[int] | None = None,
) -> ConversionResult:
    """Convert a bank-statement PDF to CSV, entirely on the local machine.

    ``strategy`` is one of ``"auto"`` (tables first, then text), ``"table"``, or
    ``"text"``. When ``csv_path`` is given the CSV is written there; the CSV text
    is always returned in :class:`ConversionResult` as well.
    """
    if strategy not in {"auto", "table", "text"}:
        raise ValueError(
            f"Unknown strategy {strategy!r}; use 'auto', 'table', or 'text'"
        )

    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"PDF not found: {source}")

    # Imported lazily so the pure parsing logic can be used/tested without pdfplumber.
    import pdfplumber

    try:
        pdf = pdfplumber.open(str(source))
    except Exception as exc:  # non-PDF / corrupt file -> clear, tool-level error
        raise ValueError(f"Could not read {source} as a PDF: {exc}") from exc

    rows: list[StatementRow] = []
    with pdf:
        if pages is None:
            selected = pdf.pages
        else:
            available = len(pdf.pages)
            out_of_range = [i for i in pages if i < 0 or i >= available]
            if out_of_range:
                raise IndexError(
                    f"pages {out_of_range} out of range; "
                    f"PDF has {available} page(s) (0-indexed)"
                )
            selected = [pdf.pages[i] for i in pages]

        for page in selected:
            page_rows: list[StatementRow] = []

            if strategy in {"auto", "table"}:
                tables = page.extract_tables() or []
                page_rows = parse_tables(
                    tables,
                    currency=currency,
                    date_formats=date_formats,
                    dayfirst=dayfirst,
                )

            if not page_rows and strategy in {"auto", "text"}:
                text = page.extract_text() or ""
                page_rows = parse_text(
                    text.splitlines(),
                    currency=currency,
                    date_formats=date_formats,
                    dayfirst=dayfirst,
                )

            rows.extend(page_rows)

    csv_text = to_csv(rows)
    out_path: Path | None = None
    if csv_path is not None:
        out_path = Path(csv_path)
        out_path.write_text(csv_text, encoding="utf-8")

    return ConversionResult(rows=rows, csv_text=csv_text, csv_path=out_path)
