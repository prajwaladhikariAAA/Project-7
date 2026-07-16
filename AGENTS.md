# AGENTS.md

## Project overview

`Project-7` is data-tech tooling for accounting firms, organized as a **`uv`
workspace monorepo**:

- `packages/core/` — `accounting-core`: shared `Money`, domain models, and the
  `ToolRegistry` that links tools together.
- `tools/<tool>/` — one standalone package per tool (currently `ledger_reconciler`
  and `tax_calculator`). Each depends on `accounting-core` and registers itself via
  an `accounting.tools` entry point so `load_installed_tools()` can discover it
  without a hard import.
- `.cursor/skills/` — a Cursor skill per tool plus the `create-accounting-tool`
  meta-skill describing how to scaffold new tools + skills.

## Standard commands

Run from the repo root (see `README.md`):

- Sync/link everything: `uv sync`
- Test: `uv run pytest`
- Lint: `uv run ruff check .` (autofix: `uv run ruff check --fix .`)

To add a tool, follow `.cursor/skills/create-accounting-tool/SKILL.md`.

## Cursor Cloud specific instructions

- Package manager is **`uv`** (installed to `~/.local/bin`, added to PATH via
  `~/.bashrc`). If `uv` is not found in a fresh shell, run
  `export PATH="$HOME/.local/bin:$PATH"`.
- `uv sync` creates the `.venv` and installs all workspace members **editable**, so
  source edits to any tool or to `accounting-core` are picked up without re-syncing.
- Re-run `uv sync` only after changing dependencies or adding/removing a workspace
  member (a new `tools/*` or `packages/*` package, or a new `accounting.tools`
  entry point). Entry-point changes are not picked up until the package is
  reinstalled via `uv sync`.
- Always run tools through `uv run ...` so the workspace virtualenv is used.
- This is a library/CLI codebase with no GUI or long-running services; validate
  changes with `uv run pytest` and `uv run ruff check .`.
