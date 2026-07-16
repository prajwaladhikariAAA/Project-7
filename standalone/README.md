# Standalone converter (no server, no install)

`statement_converter.html` is a **single, self-contained file** that converts a
bank-statement PDF to CSV/JSON entirely in your browser. It bundles the PDF engine
(pdf.js) and the parsing + balance-verification logic, so it works **100% offline**
— nothing is uploaded anywhere.

## Use it

1. Download `statement_converter.html` to your PC.
2. **Double-click it** (or open it in Chrome/Edge/Firefox). No Python, no server.
3. Wait for the status to say “Ready”, choose a PDF, click **Convert**, then
   **Download CSV** / **Download JSON**.

Tip: optionally set an **Opening balance** (the balance before the first line) to
verify the whole statement, and tick **Day-first dates** for `DD/MM/YYYY` statements.

## How it relates to the tool

The standalone mirrors the Python `pdf_statement_converter` tool's text parsing and
balance verification. The full Python tool/web app additionally supports ruled-table
(debit/credit column) extraction; the standalone uses text-line parsing, which covers
most text-based statements. Scanned/image-only PDFs (needing OCR) are not supported in
either.

## Rebuild

The file is generated. To rebuild after editing `parser.js` or `app.template.html`,
or after refreshing `vendor/` (pdf.js):

```bash
python standalone/build.py
```

`build.py` inlines `parser.js` and base64-embeds `vendor/pdf.min.js` and
`vendor/pdf.worker.min.js` into `statement_converter.html`. `parser.js` has no
dependencies and can be unit-tested with Node.
