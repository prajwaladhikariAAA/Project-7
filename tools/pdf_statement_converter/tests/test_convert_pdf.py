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


def _make_text_pdf(path: str, lines: list[str], pages: int = 1) -> None:
    c = reportlab_canvas.Canvas(path)
    for _ in range(pages):
        text = c.beginText(50, 800)
        text.setFont("Courier", 11)
        for line in lines:
            text.textLine(line)
        c.drawText(text)
        c.showPage()
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


def test_empty_pdf_yields_header_only_csv(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    _make_text_pdf(str(pdf_path), ["ACME BANK", "No transactions this period."])

    result = convert(pdf_path)

    assert result.rows == []
    assert result.csv_text.strip() == "date,description,amount,balance,currency"


def test_multipage_pdf_collects_all_rows(tmp_path):
    pdf_path = tmp_path / "multi.pdf"
    _make_text_pdf(
        str(pdf_path),
        ["Date        Description   Amount", "01/05/2026  Deposit       100.00"],
        pages=3,
    )

    result = convert(pdf_path, strategy="text")

    assert len(result.rows) == 3


def test_pages_out_of_range_raises(tmp_path):
    pdf_path = tmp_path / "one_page.pdf"
    _make_text_pdf(str(pdf_path), ["01/05/2026  Deposit  100.00"])

    with pytest.raises(IndexError, match="out of range"):
        convert(pdf_path, pages=[5])


def test_auto_strategy_reads_ruled_table(tmp_path):
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    pdf_path = tmp_path / "table.pdf"
    doc = SimpleDocTemplate(str(pdf_path))
    data = [
        ["Date", "Details", "Debit", "Credit", "Balance"],
        ["01/05/2026", "Invoice 1001", "", "1,200.00", "5,200.00"],
        ["01/09/2026", "Office supplies", "42.00", "", "5,158.00"],
    ]
    table = Table(data)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([table])

    result = convert(pdf_path, strategy="auto")

    assert len(result.rows) == 2
    assert result.rows[0].amount == Money.of("1200.00")
    assert result.rows[1].amount == Money.of("-42.00")
