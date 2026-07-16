---
name: pdf-statement-converter
description: Use and extend the pdf-statement-converter tool, which converts a bank statement PDF into a CSV of transactions, fully offline. Use when converting bank/credit-card statement PDFs to CSV, extracting transactions from PDFs, or working in tools/pdf_statement_converter.
---

# PDF Statement Converter

Located at `tools/pdf_statement_converter/`. Reads a bank-statement PDF from local
disk and writes a CSV of transactions. Runs **entirely offline** (`pdfplumber`);
no data leaves the machine.

## Usage

```python
from pdf_statement_converter import convert

result = convert("statement.pdf", "statement.csv")   # csv_path is optional
result.rows        # list[StatementRow] (date, description, amount: Money, balance)
result.csv_text    # the CSV as a string
result.csv_path    # Path written to, or None
```

Tuning knobs: `strategy` (`"auto"` | `"table"` | `"text"`), `currency`,
`dayfirst=True` (for DD/MM dates), `date_formats=[...]`, `pages=[0, 1]`.

CSV columns: `date,description,amount,balance,currency`.

## Architecture (keep this split)

- `parsing.py` — **pure** functions (no PDF): `parse_amount`, `extract_leading_date`,
  `parse_line`, `parse_text`, `parse_tables`. Add/adjust parsing here and cover it
  with plain-string tests — no PDF needed.
- `converter.py` — the only module that imports `pdfplumber`. Extracts text/tables
  per page and delegates to `parsing.py`.

## Errors & limitations

- `convert()` raises `FileNotFoundError` (missing path), `ValueError` (corrupt /
  non-PDF, or bad `strategy`), and `IndexError` (`pages` out of range). A statement
  with no recognizable transactions yields 0 rows + a header-only CSV.
- Amounts must include cents (two decimals); whole-number amounts are ignored by
  design. Scanned/image-only PDFs (need OCR) and multi-line descriptions are not
  handled.

## Extending

- New bank layout? Prefer a new/adjusted heuristic in `parsing.py`; add cases to
  `tests/test_parsing.py`.
- Real-PDF coverage lives in `tests/test_convert_pdf.py` and error handling in
  `tests/test_errors.py`. Real-PDF tests generate PDFs via `reportlab` (a dev
  dependency) and skip if it is unavailable.
- Keep `convert()`, `to_csv()`, and `StatementRow` stable; update this skill when
  behaviour changes.
