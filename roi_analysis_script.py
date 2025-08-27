import json
import pathlib
import subprocess

import xmltodict


cov_xml = pathlib.Path("logs/verify/coverage_now.xml").read_text()
cov = xmltodict.parse(cov_xml)
lines = {}

# Extract coverage data
if "packages" in cov["coverage"]:
    packages = cov["coverage"]["packages"]
    if packages:
        if isinstance(packages["package"], list):
            package_list = packages["package"]
        else:
            package_list = [packages["package"]]

        for pkg in package_list:
            if "classes" in pkg and pkg["classes"]:
                if isinstance(pkg["classes"]["class"], list):
                    class_list = pkg["classes"]["class"]
                else:
                    class_list = [pkg["classes"]["class"]]

                for cls in class_list:
                    fn = cls["@filename"]
                    if "lines" in cls and cls["lines"]:
                        line_data = cls["lines"]["line"]
                        if isinstance(line_data, list):
                            covered = sum(1 for ln in line_data if int(ln["@hits"]) > 0)
                            total = len(line_data)
                        else:
                            covered = 1 if int(line_data["@hits"]) > 0 else 0
                            total = 1
                        lines[fn] = (total, covered)

# radon cc
try:
    cc = subprocess.run(["radon", "cc", "-s", "-j", "src"], capture_output=True, text=True).stdout
    ccj = json.loads(cc) if cc else {}
except Exception:
    ccj = {}

def score(fn):
    total, covered = lines.get(fn, (0, 0))
    gap = total - covered
    comp = 0
    for k, v in ccj.items():
        if k.endswith(fn) or fn.endswith(k):
            comp += sum({"A": 1, "B": 2, "C": 3, "D": 5, "E": 8, "F": 13}.get(i["rank"], 1) for i in v)
    return (gap * (1 + comp)), gap, comp, total, covered


candidates = []
for fn in lines:
    if fn.startswith("src/") and lines[fn][0] > 0:
        candidates.append((fn,) + score(fn))

candidates.sort(key=lambda x: -x[1])
top = [
    {
        "file": c[0],
        "roi": c[1],
        "gap": c[2],
        "complexity": c[3],
        "total": c[4],
        "covered": c[5]
    }
    for c in candidates[:10]
]

pathlib.Path("logs/verify/top_roi.json").write_text(json.dumps(top, indent=2))
print("TOP_READY", len(top))
