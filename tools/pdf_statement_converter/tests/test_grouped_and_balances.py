from datetime import date

from accounting_core import Money
from pdf_statement_converter import parse_tables, parse_text, verify_balances


def test_grouped_by_date_carries_date_forward():
    lines = [
        "Date        Description              Amount     Balance",
        "01/05/2026  ACME deposit             1,200.00   6,200.00",
        "            Coffee shop                (4.50)   6,195.50",
        "            Parking                    (8.00)   6,187.50",
        "01/07/2026  Payroll                 -2,000.00   4,187.50",
    ]
    rows = parse_text(lines)

    assert [r.date for r in rows] == [
        date(2026, 1, 5),
        date(2026, 1, 5),
        date(2026, 1, 5),
        date(2026, 1, 7),
    ]
    assert [str(r.amount.amount) for r in rows] == ["1200.00", "-4.50", "-8.00", "-2000.00"]


def test_carry_date_disabled_ignores_continuation_lines():
    lines = [
        "01/05/2026  ACME deposit   1,200.00  6,200.00",
        "            Coffee shop      (4.50)  6,195.50",
    ]
    rows = parse_text(lines, carry_date=False)
    assert len(rows) == 1


def test_summary_lines_not_captured_when_carrying_date():
    lines = [
        "01/05/2026  ACME deposit   1,200.00  6,200.00",
        "            Coffee shop      (4.50)  6,195.50",
        "Total debits             2,004.50",
        "Closing balance                     6,195.50",
    ]
    rows = parse_text(lines)
    assert len(rows) == 2  # the Total/Closing lines are ignored


def test_table_carries_blank_date_cells():
    tables = [[
        ["Date", "Details", "Amount", "Balance"],
        ["01/05/2026", "ACME deposit", "1,200.00", "6,200.00"],
        ["", "Coffee shop", "-4.50", "6,195.50"],
        ["", "Parking", "-8.00", "6,187.50"],
    ]]
    rows = parse_tables(tables)
    assert len(rows) == 3
    assert all(r.date == date(2026, 1, 5) for r in rows)


def test_verify_balances_passes_for_consistent_statement():
    lines = [
        "01/05/2026  ACME deposit   1,200.00  6,200.00",
        "            Coffee shop      (4.50)  6,195.50",
        "01/07/2026  Payroll       -2,000.00  4,195.50",
    ]
    rows = parse_text(lines)
    check = verify_balances(rows, opening_balance=Money.of("5000.00"))

    assert check.ok
    assert check.checked == 3
    assert check.discrepancies == []


def test_verify_balances_detects_wrong_amount():
    # Second row's amount is wrong for its balance (should be -4.50, not -40.50).
    lines = [
        "01/05/2026  ACME deposit   1,200.00  6,200.00",
        "            Coffee shop     (40.50)  6,195.50",
        "01/07/2026  Payroll       -2,000.00  4,195.50",
    ]
    rows = parse_text(lines)
    check = verify_balances(rows, opening_balance=Money.of("5000.00"))

    assert not check.ok
    assert len(check.discrepancies) == 1
    d = check.discrepancies[0]
    assert d.index == 1
    assert d.expected_balance == Money.of("6159.50")
    assert d.actual_balance == Money.of("6195.50")
    assert d.difference == Money.of("36.00")


def test_verify_without_opening_seeds_from_first_balance():
    rows = parse_text([
        "01/05/2026  ACME deposit   1,200.00  6,200.00",
        "01/07/2026  Payroll       -2,000.00  4,200.00",
    ])
    check = verify_balances(rows)

    assert check.ok
    assert check.checked == 1  # first row seeds; second is verified
