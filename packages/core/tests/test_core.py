import pytest
from accounting_core import Money, ToolRegistry, load_installed_tools
from accounting_core.registry import Tool


def test_money_avoids_float_rounding():
    assert Money.of(0.1) + Money.of(0.2) == Money.of("0.30")


def test_money_rejects_mixed_currencies():
    with pytest.raises(ValueError):
        Money.of("1", "USD") + Money.of("1", "EUR")


def test_money_scalar_multiply():
    assert Money.of("100.00") * "0.20" == Money.of("20.00")


def test_registry_rejects_duplicates():
    reg = ToolRegistry()
    tool = Tool(name="demo", summary="", run=lambda: None)
    reg.register(tool)
    with pytest.raises(ValueError):
        reg.register(tool)


def test_installed_tools_are_discovered():
    # Both workspace tools advertise themselves via entry points, so the core can
    # link them without importing either package directly.
    discovered = load_installed_tools()
    assert {"ledger_reconciler", "tax_calculator"} <= set(discovered.names())
