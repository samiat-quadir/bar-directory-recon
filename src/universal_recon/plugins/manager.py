from __future__ import annotations

from typing import List

from .interface import PluginProtocol


class PluginManager:
    def __init__(self) -> None:
        self._plugins: List[PluginProtocol] = []

    def register(self, plugin: PluginProtocol) -> None:
        self._plugins.append(plugin)

    def run_all(self, config: dict) -> list:
        results = []
        for p in self._plugins:
            results.append(p.run(config))
        return results
