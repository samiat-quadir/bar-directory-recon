import importlib
import pkgutil

def load_plugins():
    import universal_recon.plugins as p
    for m in pkgutil.iter_modules(p.__path__):
        if m.name not in {"base", "loader"}:
            yield importlib.import_module(f"{p.__name__}.{m.name}")
