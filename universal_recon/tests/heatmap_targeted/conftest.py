import pathlib
import sys

# Ensure src/* modules can be imported
root = pathlib.Path(__file__).resolve().parents[3]
src = root / "src"
if src.exists():
    sys.path.insert(0, str(src))
