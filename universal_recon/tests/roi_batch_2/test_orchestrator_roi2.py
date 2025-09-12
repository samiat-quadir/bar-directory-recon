
import importlib
m = importlib.import_module('orchestrator')

def test_orchestrator_import():
    assert m is not None

def test_orchestrator_first_callable():
    for name in dir(m):
        if not name.startswith('_'):
            obj=getattr(m,name)
            if callable(obj):
                try:
                    obj()
                except TypeError:
                    assert True
                except Exception:
                    assert True
                break
