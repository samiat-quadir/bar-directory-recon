import xml.etree.ElementTree as ET
import pathlib
import json

# Find latest coverage XML
cov = sorted(pathlib.Path("logs/nightly").glob("*/coverage_after_fast.xml"))[-1]
root = ET.parse(cov).getroot()

items = []
for cls in root.findall(".//class"):
    fn = cls.get("filename")
    total = covered = 0
    for ln in cls.findall(".//line"):
        total += 1
        if int(ln.get("hits", "0")) > 0:
            covered += 1
    if total:
        items.append({
            "file": fn,
            "covered": covered, 
            "total": total,
            "gap": 1 - (covered / total)
        })

items.sort(key=lambda x: (-x["gap"], -x["total"]))
pathlib.Path("logs/nightly/gap_top50.json").write_text(
    json.dumps(items[:50], indent=2)
)
print(f"WROTE gap_top50.json with {len(items[:50])} items")