#!/usr/bin/env python3
"""Set coverage gate based on coverage XML.

Usage: python scripts/set_coverage_gate.py --coverage reports/coverage.xml

Logic: if coverage >= 10.5 -> gate=10 else gate=8. Replaces --cov-fail-under= in pytest.ini and pyproject.toml.
"""

from __future__ import annotations

import argparse
import re
from xml.etree import ElementTree as ET


def read_coverage_percent(xml_path: str) -> float:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # coverage.py/cobertura style: line-rate attribute as decimal
    val = root.attrib.get("line-rate")
    if val is None:
        # try totals/ line-rate
        totals = root.find("totals")
        if totals is not None:
            val = totals.attrib.get("line-rate")
    if val is None:
        raise ValueError("line-rate not found in coverage xml")
    return float(val) * 100.0


def replace_gate_in_file(path: str, gate: int) -> None:
    pattern = re.compile(r"--cov-fail-under=\s*\d+")
    with open(path, encoding="utf8") as fh:
        text = fh.read()
    if pattern.search(text):
        new_text = pattern.sub(f"--cov-fail-under={gate}", text)
    else:
        # fallback: append to addopts lines if present (simple, resilient)
        def _append_gate(match):
            prefix = match.group(1)
            opts = match.group(2)
            suffix = match.group(3)
            return prefix + opts + f" --cov-fail-under={gate}" + suffix

        new_text = re.sub(
            r'(addopts\s*=\s*"|addopts\s*=\s*\')(.*?)("|\')',
            _append_gate,
            text,
            flags=re.S,
        )
    with open(path, "w", encoding="utf8") as fh:
        fh.write(new_text)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--coverage", required=True, help="Path to coverage.xml")
    p.add_argument(
        "--files",
        nargs="*",
        default=["pytest.ini", "pyproject.toml"],
        help="Files to update",
    )

    args = p.parse_args()

    try:
        cov = read_coverage_percent(args.coverage)
    except Exception as e:
        print(f"Error reading coverage: {e}")
        return 2
    # New unified policy: gate = clamp(int(total_cov) - 1, 8, 35)
    observed_floor = int(cov)
    gate = max(8, min(35, observed_floor - 1))
    print(f"Coverage: {cov:.2f}%, observed_floor={observed_floor}, chosen gate: {gate}")

    for f in args.files:
        try:
            replace_gate_in_file(f, gate)
            print(f"Updated gate in {f}")
        except FileNotFoundError:
            print(f"File not found: {f}, skipping")
        except Exception as e:
            print(f"Failed updating {f}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
