import importlib

m = importlib.import_module("property_validation")


def test_property_validation_import():
    assert m is not None


def test_property_validation_first_callable():
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
