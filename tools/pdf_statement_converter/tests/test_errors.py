"""Error-handling tests that do not require a PDF-generation library."""

from __future__ import annotations

import pytest
from pdf_statement_converter import convert, to_csv


def test_missing_file_raises_filenotfound(tmp_path):
    with pytest.raises(FileNotFoundError, match="PDF not found"):
        convert(tmp_path / "nope.pdf")


def test_corrupt_pdf_raises_clear_value_error(tmp_path):
    bad = tmp_path / "not_a_pdf.pdf"
    bad.write_text("this is not a pdf at all")
    with pytest.raises(ValueError, match="Could not read"):
        convert(bad)


def test_invalid_strategy_raises_before_reading(tmp_path):
    # Strategy is validated before any file access, so a missing path is irrelevant.
    with pytest.raises(ValueError, match="Unknown strategy"):
        convert(tmp_path / "whatever.pdf", strategy="magic")


def test_to_csv_of_empty_rows_is_header_only():
    assert to_csv([]).strip() == "date,description,amount,balance,currency"
