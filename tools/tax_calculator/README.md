# tax-calculator

Computes sales tax / VAT on a net amount, or across a set of invoice line items.

```python
from tax_calculator import calculate_tax, LineItem

invoice = calculate_tax([
    LineItem("Consulting", "1000.00", rate="0.20"),
    LineItem("Software",   "250.00",  rate="0.10"),
])
print(invoice.net, invoice.tax, invoice.gross)
```

Rates are fractions (`0.20` == 20%). All math uses `accounting_core.Money`.
