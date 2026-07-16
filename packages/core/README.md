# accounting-core

Shared foundation for every tool in this monorepo. Depend on it from a tool with
`accounting-core` (already wired as a workspace source).

It provides:

- `Money` — a `Decimal`-backed money type that avoids float rounding errors.
- `Transaction` — the common domain model tools exchange.
- `Tool` / `ToolRegistry` — the registry that links independent tools so they can
  be discovered and invoked uniformly (via Python entry points, no hard imports).

See the repository root `README.md` for the overall architecture.
