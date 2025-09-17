#!/usr/bin/env python3
import json
import pathlib
import shlex
import subprocess
import sys

import xmltodict

logdir = pathlib.Path("logs/roi2")
logdir.mkdir(parents=True, exist_ok=True)
covf = logdir / "coverage_now.xml"
if not covf.exists():
    print("No coverage xml at", covf)
    sys.exit(0)
with covf.open() as fh:
    cov = xmltodict.parse(fh.read())

byfile = {}
pkg_node = cov["coverage"].get("packages", {})
classes_list = []
if "package" in pkg_node:
    pkg = pkg_node["package"]
    # package may contain classes directly
    if isinstance(pkg, list):
        for p in pkg:
            cls = p.get("classes", {}).get("class", [])
            if isinstance(cls, dict):
                classes_list.append(cls)
            else:
                classes_list.extend(cls)
    else:
        cls = pkg.get("classes", {}).get("class", [])
        if isinstance(cls, dict):
            classes_list.append(cls)
        else:
            classes_list.extend(cls)
else:
    classes_list = []

for cls in classes_list:
    fn = cls.get("@filename")
    lines_node = cls.get("lines") or {}
    lines = lines_node.get("line") or []
    if isinstance(lines, dict):
        lines = [lines]
    tot = len(lines)
    covd = sum(1 for ln in lines if int(ln.get("@hits", 0)) > 0)
    byfile[fn] = (tot, covd)

try:
    cc = subprocess.run(
        shlex.split("radon cc -s -j src"), capture_output=True, text=True
    )
    ccj = json.loads(cc.stdout) if cc.stdout else {}
except Exception:
    ccj = {}


def comp_score(items):
    mapping = {"A": 1, "B": 2, "C": 3, "D": 5, "E": 8, "F": 13}
    return sum(mapping.get(x.get("rank", "C"), 3) for x in items)


cands = []
for fn, (tot, covd) in byfile.items():
    if not fn or not fn.startswith("") or tot == 0:
        continue
    # Normalize filename to repo-relative
    if fn.startswith("/") or fn.startswith("C:"):
        # keep as-is
        pass
    gap = tot - covd
    comp = 0
    for k, v in ccj.items():
        if fn.endswith(k) or k.endswith(pathlib.Path(fn).name):
            comp += comp_score(v)
    roi = gap * (1 + comp)
    cands.append(
        {
            "file": fn if fn.startswith("src/") else f"src/{fn}",
            "roi": roi,
            "gap": gap,
            "complexity": comp,
            "total": tot,
            "covered": covd,
        }
    )

cands.sort(key=lambda x: (-x["roi"], -x["gap"], -x["complexity"]))
out = logdir / "top_roi.json"
out.write_text(json.dumps(cands[:10], indent=2))
print("WROTE", out)
