from datetime import date

from accounting_core import Money, Transaction
from ledger_reconciler import get_tool, reconcile


def _txn(amount, ref=None, day=5, desc="txn"):
    return Transaction(date(2026, 1, day), desc, Money.of(amount), ref)


def test_matches_by_reference():
    bank = [_txn("1200.00", ref="INV-1001")]
    book = [_txn("1200.00", ref="INV-1001", desc="Invoice 1001")]

    result = reconcile(bank, book)

    assert result.is_balanced
    assert len(result.matched) == 1
    assert not result.unmatched_bank
    assert not result.unmatched_book


def test_matches_by_amount_and_date_when_no_reference():
    bank = [_txn("50.00")]
    book = [_txn("50.00", desc="cash sale")]

    result = reconcile(bank, book)

    assert result.is_balanced


def test_reports_unmatched_on_both_sides():
    bank = [_txn("100.00", ref="A"), _txn("30.00", ref="B")]
    book = [_txn("100.00", ref="A"), _txn("75.00", ref="C")]

    result = reconcile(bank, book)

    assert not result.is_balanced
    assert [t.reference for t in result.unmatched_bank] == ["B"]
    assert [t.reference for t in result.unmatched_book] == ["C"]
    assert result.unmatched_bank_total() == Money.of("30.00")
    assert result.unmatched_book_total() == Money.of("75.00")


def test_tool_descriptor_is_exposed():
    tool = get_tool()
    assert tool.name == "ledger_reconciler"
    assert tool.run is reconcile
