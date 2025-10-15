#!/usr/bin/env python
"""Minimal CLI stub for the Bar Directory Recon toolkit."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bdr",
        description="Bar Directory Recon CLI stub. Commands are placeholders for the upcoming SDK wiring.",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    def add_stub(name: str) -> None:
        sub = subparsers.add_parser(name)
        sub.add_argument("--input", "-i", help="Input path (optional)")
        sub.add_argument("--output", "-o", help="Output path (optional)")

    for action in ("ingest", "normalize", "validate", "score", "report"):
        add_stub(action)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload: dict[str, Any] = {
        "cmd": args.cmd,
        "input": getattr(args, "input", None),
        "output": getattr(args, "output", None),
        "status": "placeholder",
    }

    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
