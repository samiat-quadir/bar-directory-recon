from __future__ import annotations

from .interface import PluginProtocol


class ExamplePlugin:
    name = "example"

    def run(self, config: dict) -> dict:
        # trivial example behavior
        return {"name": self.name, "received_keys": list(config.keys())}


