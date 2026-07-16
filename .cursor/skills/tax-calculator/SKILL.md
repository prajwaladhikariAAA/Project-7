---
name: tax-calculator
description: Use and extend the tax-calculator tool, which computes sales tax / VAT for invoice line items. Use when calculating tax, VAT, or gross/net invoice totals, or working in tools/tax_calculator.
---

# Tax Calculator

Located at `tools/tax_calculator/`. Computes net, tax, and gross totals across
invoice line items using `accounting_core.Money`.

## Usage

```python
from tax_calculator import calculate_tax, LineItem

invoice = calculate_tax([
    LineItem("Consulting", "1000.00", rate="0.20"),  # 20% VAT
    LineItem("Software",   "250.00",  rate="0.10"),  # 10% VAT
])
invoice.net    # Money 1250.00
invoice.tax    # Money 225.00
invoice.gross  # Money 1475.00
```

## Rules

- `rate` is a fraction (`0.20` == 20%); default `0` means tax-free.
- Tax is computed and rounded per line item, then summed.

## Extending

Keep `calculate_tax()` and `LineItem` stable. Add per-jurisdiction rate tables or
tax categories in `calculator.py`, cover them with tests in
`tools/tax_calculator/tests/`, and update this skill when behaviour changes.
