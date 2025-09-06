from __future__ import annotations

from typing import Protocol, Any


class PluginProtocol(Protocol):
    """Minimal protocol all plugins should follow."""

    name: str

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        ...

