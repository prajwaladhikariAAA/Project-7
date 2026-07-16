"""The registry that links independent tools together.

Each tool is a standalone package, but it advertises a small :class:`Tool`
descriptor through a Python entry point in the ``accounting.tools`` group. The
core can then discover every installed tool without importing it directly, which
keeps tools decoupled while still letting them be listed, wired into a CLI/UI, or
called by one another later.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Any

#: Entry-point group tools register themselves under.
ENTRY_POINT_GROUP = "accounting.tools"


@dataclass(frozen=True)
class Tool:
    """A uniform descriptor every tool exposes so it can be linked."""

    name: str
    summary: str
    run: Callable[..., Any]
    version: str = "0.1.0"


class ToolRegistry:
    """An in-memory collection of registered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def all(self) -> list[Tool]:
        return [self._tools[name] for name in self.names()]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)


#: A process-wide default registry tools may register into directly.
registry = ToolRegistry()


def load_installed_tools() -> ToolRegistry:
    """Discover every installed tool via the ``accounting.tools`` entry points."""
    discovered = ToolRegistry()
    for entry_point in entry_points(group=ENTRY_POINT_GROUP):
        factory = entry_point.load()
        discovered.register(factory())
    return discovered
