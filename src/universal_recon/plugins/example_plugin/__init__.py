from typing import Dict, Iterable
class _Example:
    name="example_plugin"
    def fetch(self, query: Dict) -> Iterable[Dict]:
        q=query.get("q","demo")
        yield {"source": self.name, "q": q, "example": True}
PLUGIN=_Example()
