from typing import Dict, Protocol
from collections.abc import Iterable


class SourcePlugin(Protocol):
    name: str

    def fetch(self, query: dict) -> Iterable[dict]: ...
