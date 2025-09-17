from typing import Dict
from collections.abc import Iterable


class _Example:
    name = "example_plugin"

    def fetch(self, query: dict) -> Iterable[dict]:
        q = query.get("q", "demo")
        yield {"source": self.name, "q": q, "example": True}


PLUGIN = _Example()
