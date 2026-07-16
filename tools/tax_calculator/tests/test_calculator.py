from accounting_core import Money
from tax_calculator import LineItem, calculate_tax, get_tool


def test_single_line_vat():
    result = calculate_tax([LineItem("Consulting", "1000.00", rate="0.20")])

    assert result.net == Money.of("1000.00")
    assert result.tax == Money.of("200.00")
    assert result.gross == Money.of("1200.00")


def test_multiple_lines_with_different_rates():
    result = calculate_tax([
        LineItem("Consulting", "1000.00", rate="0.20"),
        LineItem("Software", "250.00", rate="0.10"),
    ])

    assert result.net == Money.of("1250.00")
    assert result.tax == Money.of("225.00")
    assert result.gross == Money.of("1475.00")


def test_zero_rate_is_tax_free():
    result = calculate_tax([LineItem("Exempt goods", "99.99")])

    assert result.tax == Money.of("0.00")
    assert result.gross == result.net


def test_tool_descriptor_is_exposed():
    tool = get_tool()
    assert tool.name == "tax_calculator"
    assert tool.run is calculate_tax
