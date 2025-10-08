import json
import pathlib
import re

root = pathlib.Path(".")
pi = root / "pytest.ini"
markers_ok = addopts_ok = False
if pi.exists():
    s = pi.read_text()
    markers_ok = bool(re.search(r"markers\s*=.*slow", s, re.S))
    addopts_ok = "not slow" in s
docs = [
    pathlib.Path("README.md"),
    pathlib.Path("API.md"),
    pathlib.Path("DEVELOPMENT.md"),
    pathlib.Path("SECURITY.md"),
    pathlib.Path("COMPREHENSIVE_AUDIT_COMPLETION_REPORT.md"),
]
docs_present = {p.name: p.exists() for p in docs}
ignore_ok = False
gi = root / ".gitignore"
if gi.exists():
    g = gi.read_text()
    ignore_ok = all(
        x in g
        for x in [
            "logs/",
            ".coverage",
            "monitoring/alertmanager/alertmanager.local.yml",
        ]
    )
result = {
    "markers_ok": markers_ok,
    "addopts_ok": addopts_ok,
    "docs_present": docs_present,
    "ignore_ok": ignore_ok,
}
with open("logs/verify/config_checks.json", "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result))
