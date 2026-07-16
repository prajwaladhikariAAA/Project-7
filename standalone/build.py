#!/usr/bin/env python3
"""Assemble the self-contained standalone HTML.

Inlines the browser parser and base64-encodes the vendored pdf.js engine so the
resulting `statement_converter.html` runs fully offline by simply opening it in a
browser (no server, no network). Re-run after changing `parser.js`,
`app.template.html`, or the files in `vendor/`.

Usage:  python build.py
"""

from __future__ import annotations

import base64
from pathlib import Path

HERE = Path(__file__).parent


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    template = (HERE / "app.template.html").read_text(encoding="utf-8")
    parser_js = (HERE / "parser.js").read_text(encoding="utf-8")
    pdf_main = _b64(HERE / "vendor" / "pdf.min.js")
    pdf_worker = _b64(HERE / "vendor" / "pdf.worker.min.js")

    html = (
        template.replace("/*__PARSER_JS__*/", parser_js)
        .replace("__PDF_MAIN_B64__", pdf_main)
        .replace("__PDF_WORKER_B64__", pdf_worker)
    )

    out = HERE / "statement_converter.html"
    out.write_text(html, encoding="utf-8")
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"Wrote {out} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
