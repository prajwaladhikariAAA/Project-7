"""End-to-end test against a real generated PDF (skipped if reportlab is absent)."""

from __future__ import annotations

from datetime import date

import pytest
from accounting_core import Money
from pdf_statement_converter import convert

reportlab_canvas = pytest.importorskip("reportlab.pdfgen.canvas")


def _make_statement_pdf(path: str) -> None:
    c = reportlab_canvas.Canvas(path)
    text = c.beginText(50, 800)
    text.setFont("Courier", 11)
    for line in [
        "ACME BANK - Statement",
        "Date        Description              Amount     Balance",
        "01/05/2026  ACME Corp deposit        1,200.00   5,200.00",
        "01/07/2026  Coffee shop               (4.50)    5,195.50",
        "01/09/2026  Payroll                 -2,000.00   3,195.50",
    ]:
        text.textLine(line)
    c.drawText(text)
    c.save()


def test_convert_real_pdf(tmp_path):
    pdf_path = tmp_path / "statement.pdf"
    csv_path = tmp_path / "statement.csv"
    _make_statement_pdf(str(pdf_path))

    result = convert(pdf_path, csv_path, strategy="text")

    assert csv_path.exists()
    assert len(result.rows) == 3
    assert result.rows[0].date == date(2026, 1, 5)
    assert result.rows[0].amount == Money.of("1200.00")
    assert result.rows[1].amount == Money.of("-4.50")
    assert result.rows[2].amount == Money.of("-2000.00")
    assert result.csv_text.startswith("date,description,amount,balance,currency")
