from typing import Protocol, Iterable, Dict
class SourcePlugin(Protocol):
    name: str
    def fetch(self, query: Dict) -> Iterable[Dict]: ...
