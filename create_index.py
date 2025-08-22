"""Create index of overnight quality artifacts"""
from pathlib import Path

d = sorted(Path("logs/nightly").glob("*"))[-1]
index = d / "INDEX.txt"
files = sorted(str(p) for p in d.rglob("*") if p.is_file())
index.write_text("\n".join(files))
print(f"INDEX_AT {index}")
print(f"ARTIFACT_COUNT {len(files)}")