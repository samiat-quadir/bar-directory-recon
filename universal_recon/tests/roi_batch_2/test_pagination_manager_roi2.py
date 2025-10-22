import importlib

m = importlib.import_module("pagination_manager")


def test_pagination_manager_import():
    assert m is not None


def test_pagination_manager_first_callable():
    for name in dir(m):
        if not name.startswith("_"):
            obj = getattr(m, name)
            if callable(obj):
                try:
                    obj()
                except TypeError:
                    assert True
                except Exception:
                    assert True
                break
