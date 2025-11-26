"""Minimal adapter telemetry helpers for the bdr CLI."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class AdapterStats:
    """Aggregated call stats for a single adapter."""

    calls: int = 0
    success: int = 0
    timeout: int = 0
    fallback: int = 0
    total_ms: float = 0.0


_STATS: Dict[str, AdapterStats] = {}


def record_call(name: str, outcome: str, elapsed_ms: float) -> None:
    """Record a call outcome for a named adapter."""

    stats = _STATS.setdefault(name, AdapterStats())
    stats.calls += 1
    stats.total_ms += max(elapsed_ms, 0.0)

    if outcome in ("success", "timeout", "fallback"):
        setattr(stats, outcome, getattr(stats, outcome) + 1)


def emit_if_enabled() -> None:
    """Flush adapter stats to stdout or GitHub summary when enabled."""

    if not os.getenv("BDR_ADAPTER_METRICS"):
        return

    lines = [
        "# Adapter telemetry",
        "",
        "| adapter | calls | success | timeout | fallback | avg ms |",
        "|---------|-------|---------|---------|----------|--------|",
    ]

    wrote_row = False
    for name, stats in sorted(_STATS.items()):
        avg = (stats.total_ms / stats.calls) if stats.calls else 0.0
        lines.append(
            f"| {name} | {stats.calls} | {stats.success} | {stats.timeout} | {stats.fallback} | {avg:.1f} |"
        )
        wrote_row = True

    if not wrote_row:
        lines.append("| (no adapters) | 0 | 0 | 0 | 0 | 0.0 |")

    text = "\n".join(lines) + "\n"
    summary = os.getenv("GITHUB_STEP_SUMMARY")

    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write(text)
        except OSError:
            print(text)
    else:
        print(text)
