from typing import Protocol, Dict, Any, Iterable

class Plugin(Protocol):
    name: str

    def fetch(self, **kwargs) -> Iterable[Dict[str, Any]]: ...

    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]: ...

    def validate(self, record: Dict[str, Any]) -> bool: ...
