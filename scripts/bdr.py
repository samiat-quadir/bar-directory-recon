#!/usr/bin/env python
"""CLI demo pipeline for the Bar Directory Recon toolkit."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA = Path("configs/schema.yaml")
DEFAULT_FIELDMAP = Path("configs/fieldmap.yaml")
DEFAULT_RULESET = Path("configs/ruleset.yaml")


def _warn(message: str) -> None:
    print(f"[bdr] {message}", file=sys.stderr)


def _ensure_parent(path: Path) -> None:
    if path.is_dir():
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def _optional_import(module: str) -> Any | None:
    try:
        return importlib.import_module(module)
    except Exception:
        return None


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Any) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _coerce_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [
            dict(record) if isinstance(record, dict) else {"value": record} for record in payload
        ]
    if isinstance(payload, dict):
        records = payload.get("records")
        if isinstance(records, list):
            return [
                dict(record) if isinstance(record, dict) else {"value": record}
                for record in records
            ]
    return []


def _load_yaml_optional(path: Path) -> Any | None:
    if not path.exists():
        return None
    yaml = _optional_import("yaml")
    if yaml is None:
        _warn("pyyaml not available; proceeding with built-in validation fallback.")
        return None
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _path_display(path: Path) -> str:
    absolute = path if path.is_absolute() else Path.cwd() / path
    try:
        return absolute.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return absolute.as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bdr",
        description="Bar Directory Recon CLI demo wiring for ingest → normalize → validate → score → report.",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    def add_stage(
        name: str, *, help_text: str, include_output: bool = True
    ) -> argparse.ArgumentParser:
        stage = subparsers.add_parser(name, help=help_text)
        stage.add_argument("--input", "-i", type=Path, required=True, help="Input JSON path")
        if include_output:
            stage.add_argument("--output", "-o", type=Path, required=True, help="Output JSON path")
        return stage

    add_stage("ingest", help_text="Copy source data into the working area.")
    add_stage("normalize", help_text="Attempt to normalize records using available utilities.")
    validate_parser = add_stage(
        "validate", help_text="Validate normalized records against simple contracts."
    )
    validate_parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Schema YAML (default: %(default)s)",
    )
    validate_parser.add_argument(
        "--fieldmap",
        type=Path,
        default=DEFAULT_FIELDMAP,
        help="Field map YAML (default: %(default)s)",
    )
    validate_parser.add_argument(
        "--ruleset",
        type=Path,
        default=DEFAULT_RULESET,
        help="Ruleset YAML (default: %(default)s)",
    )
    add_stage("score", help_text="Compute a simple quality score from validation output.")
    report_parser = add_stage("report", help_text="Generate JSON and Markdown summaries.")
    report_parser.add_argument(
        "--markdown",
        type=Path,
        help="Optional Markdown output path (defaults to <output>.md)",
    )

    return parser


def run_ingest(input_path: Path, output_path: Path) -> dict[str, Any]:
    records = _coerce_records(_read_json(input_path))
    if not records:
        _warn("Ingest found no records; continuing anyway.")
    _write_json(output_path, records)
    return {
        "stage": "ingest",
        "records": len(records),
        "output": _path_display(output_path),
    }


def run_normalize(input_path: Path, output_path: Path) -> dict[str, Any]:
    records = _coerce_records(_read_json(input_path))
    normalizer = _optional_import("universal_recon.utils.record_normalizer")
    normalized = records
    used_normalizer = False
    if normalizer is not None:
        for candidate in ("normalize_records", "normalize"):
            func = getattr(normalizer, candidate, None)
            if callable(func):
                try:
                    normalized = func(records)
                    used_normalizer = True
                except Exception as exc:  # pragma: no cover - defensive
                    _warn(f"Normalizer threw an exception ({exc}); using pass-through data.")
                break
        else:
            _warn(
                "record_normalizer module lacks an expected entry point; using pass-through data."
            )
    else:
        _warn("record_normalizer module not importable; using pass-through data.")
    _write_json(output_path, normalized)
    return {
        "stage": "normalize",
        "records": len(normalized),
        "used_normalizer": used_normalizer,
        "output": _path_display(output_path),
    }


def run_validate(
    input_path: Path,
    output_path: Path,
    schema_path: Path,
    fieldmap_path: Path,
    ruleset_path: Path,
) -> dict[str, Any]:
    records = _coerce_records(_read_json(input_path))
    fieldmap_cfg = _load_yaml_optional(fieldmap_path) or {}
    rules_cfg = _load_yaml_optional(ruleset_path) or {}
    schema_present = schema_path.exists()

    mapped_records = []
    mappings = fieldmap_cfg.get("mappings") if isinstance(fieldmap_cfg, dict) else None
    if isinstance(mappings, list):
        for record in records:
            mapped = {
                entry.get("target"): record.get(entry.get("source")) for entry in mappings if entry
            }
            mapped_records.append(mapped)
    else:
        mapped_records = [dict(record) for record in records]

    required_fields: set[str] = {"full_name", "bar_id"}
    if isinstance(rules_cfg, dict):
        extracted = {
            rule.get("field")
            for rule in rules_cfg.get("rules", [])
            if isinstance(rule, dict) and rule.get("require")
        }
        required_fields |= {field for field in extracted if field}

    errors: list[str] = []
    for idx, record in enumerate(mapped_records):
        missing = [field for field in required_fields if not record.get(field)]
        if missing:
            errors.append(f"record[{idx}] missing required fields: {', '.join(missing)}")

    validator = _optional_import("universal_recon.utils.record_field_validator_v3")
    if validator is not None:
        for candidate in ("validate_records", "validate"):
            func = getattr(validator, candidate, None)
            if callable(func):
                try:
                    outcome = func(mapped_records, schema_path, fieldmap_path, ruleset_path)
                    if isinstance(outcome, dict) and isinstance(outcome.get("errors"), list):
                        errors.extend(str(item) for item in outcome["errors"])
                    elif isinstance(outcome, list):
                        errors.extend(str(item) for item in outcome)
                except Exception as exc:  # pragma: no cover - defensive
                    _warn(
                        f"Validator raised an exception ({exc}); continuing with fallback results."
                    )
                break

    summary = {
        "stage": "validate",
        "records": len(mapped_records),
        "errors": len(errors),
        "details": errors,
        "schema_present": schema_present,
        "output": _path_display(output_path),
    }
    _write_json(output_path, summary)
    return summary


def run_score(input_path: Path, output_path: Path) -> dict[str, Any]:
    payload = _read_json(input_path)
    records = int(payload.get("records", 0)) if isinstance(payload, dict) else 0
    errors = int(payload.get("errors", 0)) if isinstance(payload, dict) else 0
    clean = max(records - errors, 0)
    score = 100 if records <= 0 else max(0, 100 - int((errors / records) * 100))

    histogram = {"clean": clean, "issues": errors}
    visualizer = _optional_import("universal_recon.utils.score_visualizer")
    if visualizer is not None:
        heatmap_fn = getattr(visualizer, "generate_heatmap_data", None)
        if callable(heatmap_fn) and isinstance(payload, dict):
            details = payload.get("details")
            if isinstance(details, list):
                try:
                    histogram = heatmap_fn(details)
                except Exception as exc:  # pragma: no cover - defensive
                    _warn(f"score_visualizer failed ({exc}); using fallback histogram.")

    summary = {
        "stage": "score",
        "records": records,
        "errors": errors,
        "score": score,
        "histogram": histogram,
        "output": _path_display(output_path),
    }
    _write_json(output_path, summary)
    return summary


def run_report(input_path: Path, output_path: Path, markdown_path: Path | None) -> dict[str, Any]:
    payload = _read_json(input_path)
    records = int(payload.get("records", 0)) if isinstance(payload, dict) else 0
    errors = int(payload.get("errors", 0)) if isinstance(payload, dict) else 0
    score = int(payload.get("score", 0)) if isinstance(payload, dict) else 0
    histogram = payload.get("histogram") if isinstance(payload, dict) else None

    md_path = markdown_path or output_path.with_suffix(".md")
    report = {
        "stage": "report",
        "records": records,
        "errors": errors,
        "score": score,
        "histogram": histogram or {"clean": max(records - errors, 0), "issues": errors},
        "output_json": _path_display(output_path),
        "output_markdown": _path_display(md_path),
    }

    _write_json(output_path, report)

    lines = [
        "# Demo Report",
        "",
        f"Records: {records}",
        f"Errors: {errors}",
        f"Score: {score}",
        "",
        "## Histogram",
    ]
    hist = report["histogram"]
    if isinstance(hist, dict):
        for key, value in hist.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- (histogram unavailable)")

    _ensure_parent(md_path)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.cmd == "ingest":
        return run_ingest(args.input, args.output)
    if args.cmd == "normalize":
        return run_normalize(args.input, args.output)
    if args.cmd == "validate":
        return run_validate(args.input, args.output, args.schema, args.fieldmap, args.ruleset)
    if args.cmd == "score":
        return run_score(args.input, args.output)
    if args.cmd == "report":
        return run_report(args.input, args.output, args.markdown)
    raise ValueError(f"Unknown command: {args.cmd}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = dispatch(args)
    except FileNotFoundError as exc:
        _warn(str(exc))
        return 1
    except Exception as exc:  # pragma: no cover - defensive
        _warn(f"Unexpected error: {exc}")
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
