from collections.abc import Iterable
from typing import Protocol


class SourcePlugin(Protocol):
    name: str

    def fetch(self, query: dict) -> Iterable[dict]: ...
