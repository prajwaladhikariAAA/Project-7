---
name: create-accounting-tool
description: Scaffold a new accounting-firm tool as a workspace package plus its matching Cursor skill in this monorepo. Use when adding a new tool under tools/, wiring it into the shared accounting-core registry, or when the user asks to create/add an accounting tool.
---

# Create an Accounting Tool

This monorepo hosts one **tool per folder** under `tools/`, all linked through the
shared `packages/core` package (`accounting-core`). Every tool ships with a
matching skill under `.cursor/skills/<tool-name>/` so the agent can use and extend
it. Follow these steps to add a new tool consistently.

## Conventions

- Folder + distribution name: `tools/<tool_name>/`, distribution `Name-With-Hyphens`.
- Import package: `<tool_name>` (snake_case) under a `src/` layout.
- Depend on shared code via `accounting-core` — never copy money/model logic.
- Money is always `accounting_core.Money` (Decimal-backed). Never use floats.
- Every tool exposes a `get_tool() -> accounting_core.Tool` factory and registers
  it through the `accounting.tools` entry point. This is what "links" the tool.

## Steps

Copy this checklist and track progress:

```
- [ ] 1. Create tools/<tool_name>/ with a src/ layout
- [ ] 2. Write pyproject.toml (deps + accounting.tools entry point)
- [ ] 3. Implement the tool logic in src/<tool_name>/
- [ ] 4. Expose get_tool() in src/<tool_name>/__init__.py
- [ ] 5. Add tests under tools/<tool_name>/tests/
- [ ] 6. Add the tool to the root pyproject.toml (deps + [tool.uv.sources])
- [ ] 7. Create the matching skill in .cursor/skills/<tool-name>/SKILL.md
- [ ] 8. uv sync && uv run pytest && uv run ruff check .
```

### 2. pyproject.toml template

```toml
[project]
name = "<tool-name>"
version = "0.1.0"
description = "<one line>"
requires-python = ">=3.12"
dependencies = ["accounting-core"]

[project.entry-points."accounting.tools"]
<tool_name> = "<tool_name>:get_tool"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<tool_name>"]

[tool.uv.sources]
accounting-core = { workspace = true }
```

### 4. get_tool() template

```python
from accounting_core import Tool
from .core import run  # your entry function

def get_tool() -> Tool:
    return Tool(name="<tool_name>", summary="<one line>", run=run, version="0.1.0")
```

### 6. Register in the root `pyproject.toml`

Add the distribution to `[project].dependencies` and map it in
`[tool.uv.sources]` as `{ workspace = true }`. `uv sync` then links it into the
shared virtualenv.

## Keep the skill in sync

When a tool's behaviour changes, update its `.cursor/skills/<tool-name>/SKILL.md`
in the same change so the skill always documents the current API and usage.

## Verify

Run `uv sync`, then `uv run pytest` and `uv run ruff check .` from the repo root.
Confirm `accounting_core.load_installed_tools()` lists the new tool.
