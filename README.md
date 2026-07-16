# Project-7

Data-tech tooling for accounting firms — a modular monorepo where **each tool is
its own package** and each tool is backed by a **Cursor skill** that evolves with it.

## Why this layout

Accounting firms need many small, independent tools (reconciliation, tax, payroll,
reporting…). We want each tool to be developed and shipped on its own, yet share
common building blocks and be easy to link together later. This repo achieves that
with a **`uv` workspace**:

- `packages/core/` — shared `accounting-core` library: the `Money` type, domain
  models, and the **tool registry**. This is the "link" every tool builds on.
- `tools/<tool>/` — one folder per tool, each a standalone installable package.
  Tools depend on `accounting-core` and advertise themselves through the
  `accounting.tools` **entry point**, so the core can discover and link them
  without hard imports.
- `.cursor/skills/<tool>/` — a Cursor skill per tool (plus a meta-skill,
  `create-accounting-tool`) so the agent knows how to use and extend each tool as
  it changes.

```
packages/core/                # accounting-core: Money, models, ToolRegistry
tools/ledger_reconciler/      # bank vs. ledger reconciliation
tools/tax_calculator/         # sales tax / VAT
tools/pdf_statement_converter/# bank-statement PDF -> CSV (offline)
apps/web/                     # FastAPI web UI for the PDF converter (upload -> export)
.cursor/skills/               # one skill per tool + create-accounting-tool meta-skill
```

`apps/` holds user-facing applications that compose tools; `tools/` holds the
business logic; `packages/` holds shared building blocks.

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # create .venv and link all workspace members
uv run pytest           # run all tests
uv run ruff check .     # lint
```

Discover every installed tool through the shared registry:

```bash
uv run python -c "from accounting_core import load_installed_tools as l; print([t.name for t in l().all()])"
```

Run the web app (PDF → CSV/JSON in the browser):

```bash
uv run statement-web           # http://127.0.0.1:8000
```

## Adding a new tool

Use the `create-accounting-tool` Cursor skill, or follow
`.cursor/skills/create-accounting-tool/SKILL.md`: create `tools/<tool>/`, depend on
`accounting-core`, expose a `get_tool()` factory + `accounting.tools` entry point,
register it in the root `pyproject.toml`, and add a matching skill.
