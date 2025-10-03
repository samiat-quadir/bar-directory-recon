import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

cov_path = Path("logs/nightly/coverage_first.xml")
if not cov_path.exists():
    print("coverage_first.xml not found")
    raise SystemExit(2)
cov = ET.parse(str(cov_path))
rows = []
for pkg in cov.findall(".//package"):
    for cl in pkg.findall("classes/class"):
        fn = cl.attrib.get("filename", "")
        rate = float(cl.attrib.get("line-rate", "0")) * 100
        if fn and (fn.startswith("src") or fn.startswith("universal_recon")):
            rows.append((rate, fn))
rows.sort(key=lambda x: x[0])
worst = [n for _, n in rows[:10]]
Path("logs/nightly/coverage_heatmap_top10.json").write_text(json.dumps(worst, indent=2))

outdir = Path("universal_recon/tests/auto_smoke")
outdir.mkdir(parents=True, exist_ok=True)
created = []
for idx, rel in enumerate(worst, 1):
    mod = rel.replace("/", ".")
    mod = mod.replace("\\", ".")
    mod = re.sub(r"\.py$", "", mod)
    if mod.endswith("__init__"):
        continue
    t = outdir / f"test_auto_{idx:02d}.py"
    t.write_text(
        f"""
def test_import_{idx:02d}():
    __import__("{mod}")
""",
        encoding="utf-8",
    )
    created.append(str(t))
Path("logs/nightly/auto_smoke_created.txt").write_text("\n".join(created))
print("CREATED:", len(created))
