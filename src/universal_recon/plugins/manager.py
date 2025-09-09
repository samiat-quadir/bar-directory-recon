import importlib, pkgutil
from typing import List, Dict, Iterable
from .interface import SourcePlugin
def load_plugins() -> List[SourcePlugin]:
    mods=[]
    pkg_path_list = globals().get("__path__")
    if not pkg_path_list or not isinstance(pkg_path_list, list) or not pkg_path_list:
        raise ImportError("Cannot determine package path: __path__ is missing or empty.")
    pkg_path = pkg_path_list[0]
    for m in pkgutil.iter_modules([pkg_path]):
        if m.name not in ("interface","manager"):
            mod = importlib.import_module(f".{m.name}", __name__)
            if hasattr(mod, "PLUGIN"):
                mods.append(mod.PLUGIN)
    return mods
def fanout(query: Dict) -> Iterable[Dict]:
    for p in load_plugins():
        yield from p.fetch(query)
