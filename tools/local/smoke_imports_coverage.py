#!/usr/bin/env python3
import importlib
import pathlib
import pkgutil
import sys

p = pathlib.Path("src")
if not p.exists():
    print("No src directory")
    sys.exit(0)
sys.path.insert(0, str(p.resolve()))
mods = [x.name for x in pkgutil.iter_modules([str(p)])]
print("MODULES:", mods)
for mname in mods:
    try:
        m = importlib.import_module(mname)
        for name in dir(m):
            if name.startswith("_"):
                continue
            obj = getattr(m, name)
            if callable(obj):
                try:
                    obj()
                except TypeError:
                    pass
                except Exception:
                    pass
                break
    except Exception as e:
        print("IMPORT_ERR", mname, e)
print("DONE")
