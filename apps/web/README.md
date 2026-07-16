# statement-web

A small **web app** for the `pdf_statement_converter` tool: upload a bank-statement
PDF, review the parsed transactions and balance verification, and **export to CSV or
JSON**. Runs fully offline — the PDF is processed on the server and never leaves the
machine.

## Run (development)

```bash
uv run statement-web                       # http://127.0.0.1:8000
# or, with autoreload while editing:
uv run uvicorn statement_web.app:app --reload
```

Then open http://127.0.0.1:8000, drop a PDF, and click **Convert**.

## API

- `GET /` — the single-page UI.
- `GET /api/health` — health probe.
- `POST /api/convert` — multipart form: `file` (PDF) plus optional `strategy`,
  `currency`, `dayfirst`, `opening_balance`. Returns JSON with `rows`, `csv`, and
  `balance_check`.

Export happens in the browser (CSV / JSON download) from the returned data.
