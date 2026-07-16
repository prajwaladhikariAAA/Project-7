# pdf-statement-converter

Convert a bank-statement **PDF into a CSV** of transactions — entirely offline. The
PDF is read from local disk with [`pdfplumber`](https://github.com/jsvine/pdfplumber),
parsed, and written back to a local CSV. No data ever leaves the machine, which
matters for client bank data.

```python
from pdf_statement_converter import convert

result = convert("statement.pdf", "statement.csv")
print(len(result.rows), "transactions ->", result.csv_path)
print(result.csv_text)          # also available in-memory
```

CSV columns: `date,description,amount,balance,currency`.

## How it handles real statements

- **Dates**: `MM/DD/YYYY`, `DD/MM/YYYY` (`dayfirst=True`), `YYYY-MM-DD`, `DD Mon YYYY`.
- **Amounts**: thousands separators, `$`/`£`/`€`, and negatives written as
  `-45.00`, `(45.00)`, or `45.00 DR`.
- **Layouts**: `strategy="auto"` tries table extraction first (incl. separate
  debit/credit columns) and falls back to line-based text parsing.

## Errors

- Missing path → `FileNotFoundError`.
- Non-PDF / corrupt file → `ValueError("Could not read ... as a PDF: ...")`.
- Unknown `strategy` → `ValueError`.
- `pages` index out of range → `IndexError` naming the valid range.
- A statement with no recognizable transactions → 0 rows and a header-only CSV.

## Known limitations

Statement layouts vary widely. Not handled:

- **Amounts without cents** (e.g. `1,200`): ignored on purpose — requiring two
  decimals prevents reference/account numbers from being mistaken for money.
- **Multi-line descriptions** and **scanned/image-only PDFs** (which need OCR).

Pass `date_formats=` / `dayfirst=` / `currency=` / `strategy=` / `pages=` to tune
parsing for a specific bank.
