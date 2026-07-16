from datetime import date

from accounting_core import Money
from pdf_statement_converter import get_tool, parse_tables, parse_text, to_csv
from pdf_statement_converter.parsing import extract_leading_date, parse_amount


def test_parse_amount_variants():
    assert parse_amount("1,200.00") == Money.of("1200.00")
    assert parse_amount("$1,200.00") == Money.of("1200.00")
    assert parse_amount("(45.00)") == Money.of("-45.00")
    assert parse_amount("-45.00") == Money.of("-45.00")
    assert parse_amount("45.00 DR") == Money.of("-45.00")
    assert parse_amount("45.00 CR") == Money.of("45.00")


def test_extract_leading_date_formats():
    assert extract_leading_date("2026-01-05 payroll")[0] == date(2026, 1, 5)
    assert extract_leading_date("01/05/2026 payroll")[0] == date(2026, 1, 5)
    assert extract_leading_date("05/01/2026 payroll", dayfirst=True)[0] == date(2026, 1, 5)
    assert extract_leading_date("5 Jan 2026 payroll")[0] == date(2026, 1, 5)
    assert extract_leading_date("no date here") is None


def test_parse_text_lines():
    lines = [
        "Date        Description              Amount     Balance",
        "01/05/2026  ACME Corp deposit        1,200.00   5,200.00",
        "01/07/2026  Coffee shop               (4.50)    5,195.50",
        "random footer line",
    ]
    rows = parse_text(lines)

    assert len(rows) == 2
    assert rows[0].date == date(2026, 1, 5)
    assert rows[0].description == "ACME Corp deposit"
    assert rows[0].amount == Money.of("1200.00")
    assert rows[0].balance == Money.of("5200.00")
    assert rows[1].amount == Money.of("-4.50")


def test_parse_tables_with_debit_credit_columns():
    tables = [[
        ["Date", "Details", "Debit", "Credit", "Balance"],
        ["01/05/2026", "Invoice 1001", "", "1,200.00", "5,200.00"],
        ["01/09/2026", "Office supplies", "42.00", "", "5,158.00"],
    ]]
    rows = parse_tables(tables)

    assert len(rows) == 2
    assert rows[0].amount == Money.of("1200.00")
    assert rows[1].amount == Money.of("-42.00")
    assert rows[1].description == "Office supplies"


def test_to_csv_shape():
    rows = parse_text(["01/05/2026  ACME deposit  1,200.00  5,200.00"])
    csv_text = to_csv(rows)
    header, first = csv_text.splitlines()[:2]

    assert header == "date,description,amount,balance,currency"
    assert first == "2026-01-05,ACME deposit,1200.00,5200.00,USD"


def test_tool_descriptor_is_exposed():
    tool = get_tool()
    assert tool.name == "pdf_statement_converter"
