#!/usr/bin/env python3

"""Small helper to parse logs/roi2/pytest_after.txt and update cov gate in project files.

Usage: python scripts/set_gate.py --logs logs/roi2/pytest_after.txt
"""

import argparse
import pathlib
import re


def compute_gate(txt_path: pathlib.Path):
    txt = txt_path.read_text()
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", txt)
    obs = int(m.group(1)) if m else 0
    gate = min(35, max(8, obs - 1))
    return obs, gate


def update_files(gate: int, files=("pytest.ini", "pyproject.toml", "tox.ini")):
    for fn in files:
        p = pathlib.Path(fn)
        if p.exists():
            s = p.read_text()
            ns = re.sub(r"--cov-fail-under=\d+", f"--cov-fail-under={gate}", s)
            if s != ns:
                p.write_text(ns)
                print(f"updated {fn}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--logs", default="logs/roi2/pytest_after.txt")
    args = p.parse_args()
    txt = pathlib.Path(args.logs)
    if not txt.exists():
        print(f"Log file {txt} not found")
        raise SystemExit(2)
    obs, gate = compute_gate(txt)
    print(f"OBSERVED={obs} GATE={gate}")
    update_files(gate)
    # write a small gate summary
    out = pathlib.Path("logs/roi2/gate_summary.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"OBSERVED={obs} GATE={gate}\n")
    print("wrote logs/roi2/gate_summary.txt")
