from collections.abc import Iterable
from typing import Dict


class _Example:
    name = "example_plugin"

    def fetch(self, query: dict) -> Iterable[dict]:
        q = query.get("q", "demo")
        yield {"source": self.name, "q": q, "example": True}


PLUGIN = _Example()
