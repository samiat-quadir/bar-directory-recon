import importlib, pkgutil
from typing import List, Dict, Iterable
from .interface import SourcePlugin
def load_plugins() -> List[SourcePlugin]:
    mods=[]
    pkg_path = __path__[0]  # type: ignore[name-defined]
    for m in pkgutil.iter_modules([pkg_path]):
        if m.name not in ("interface","manager"):
            mod = importlib.import_module(f".{m.name}", __name__)
            if hasattr(mod, "PLUGIN"):
                mods.append(mod.PLUGIN)
    return mods
def fanout(query: Dict) -> Iterable[Dict]:
    for p in load_plugins():
        yield from p.fetch(query)
