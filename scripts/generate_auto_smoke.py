#!/usr/bin/env python3
"""Create safe import-only auto-smoke tests from coverage XML.

This generator reads logs/nightly/coverage_first.xml and for the lowest-coverage
modules creates simple tests that only import the module to detect import errors.
"""

import pathlib
import xml.etree.ElementTree as ET

cov = pathlib.Path("logs/nightly/coverage_first.xml")
if not cov.exists():
    print("coverage XML not found; run coverage first")
    raise SystemExit(2)

root = ET.parse(cov).getroot()
ns = {"c": "http://schema."}  # not used but kept for clarity

out_dir = pathlib.Path("universal_recon/tests/auto_smoke")
out_dir.mkdir(parents=True, exist_ok=True)

modules = []
for package in root.findall("packages/package"):
    for cl in package.findall("classes/class"):
        filename = cl.get("filename")
        # Keep project files only
        if not filename.startswith("src/") and not filename.startswith("universal_recon/"):
            continue
        # convert path to module import path heuristically
        mod = filename.replace("/", ".").rstrip(".py")
        modules.append(mod)

# pick first 30 modules to keep tests small
modules = modules[:30]
for m in modules:
    test_name = m.replace(".", "_")
    path = out_dir / f"test_import_{test_name}.py"
    with path.open("w", encoding="utf8") as f:
        f.write(f"# Auto-generated import-only smoke test for {m}\n")
        f.write("try:\n")
        f.write(f"    import {m}\n")
        f.write("except Exception as e:\n")
        f.write("    raise\n")
print(f"Wrote {len(modules)} auto-smoke tests to {out_dir}")
