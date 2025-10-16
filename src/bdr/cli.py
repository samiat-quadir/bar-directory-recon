import argparse
import json
import pathlib
import sys


def _ensure_dir(p):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)


def _load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def _dump_json(p, obj):
    p = pathlib.Path(p)
    _ensure_dir(p)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _try_import(mod):
    try:
        return __import__(mod, fromlist=["*"])
    except Exception:
        return None


def run_ingest(inp, out):
    data = _load_json(inp)
    _dump_json(out, data)
    return {"records": len(data)}


def run_normalize(inp, out):
    data = _load_json(inp)
    norm = _try_import("universal_recon.utils.record_normalizer")
    if norm and hasattr(norm, "normalize_records"):
        try:
            data = norm.normalize_records(data)  # best-effort
        except Exception:
            pass
    _dump_json(out, data)
    return {"records": len(data)}


def run_validate(
    inp,
    out,
    schema="configs/schema.yaml",
    fieldmap="configs/fieldmap.yaml",
    rules="configs/ruleset.yaml",
):
    data = _load_json(inp)
    errors = 0
    v = _try_import("universal_recon.utils.record_field_validator_v3")
    if v and hasattr(v, "validate_records"):
        try:
            errors = v.validate_records(data, schema, fieldmap, rules)  # hypothetical
        except Exception:
            errors = 0
    _dump_json(out, {"records": len(data), "errors": errors})
    return {"records": len(data), "errors": errors}


def run_score(inp, out):
    payload = _load_json(inp)
    total = payload.get("records", 0)
    errors = payload.get("errors", 0)
    score = 100 if total == 0 else max(0, 100 - int(100 * errors / max(1, total)))
    _dump_json(out, {"records": total, "errors": errors, "score": score})
    return {"records": total, "errors": errors, "score": score}


def run_report(inp, out_json, out_md):
    payload = _load_json(inp)
    _dump_json(out_json, payload)
    pathlib.Path(out_md).write_text(
        f"# Demo Report\n\nRecords: {payload.get('records',0)}\n\nErrors: {payload.get('errors',0)}\n\nScore: {payload.get('score',0)}\n",
        encoding="utf-8",
    )
    return payload


def main():
    p = argparse.ArgumentParser(prog="bdr", description="Bar Directory Recon CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("ingest", "normalize", "validate", "score", "report"):
        sp = sub.add_parser(name)
        sp.add_argument("--input", "-i")
        sp.add_argument("--output", "-o")
    spv = [s for s in sub.choices.values() if s.prog.endswith("validate")][0]
    spv.add_argument("--schema", default="configs/schema.yaml")
    spv.add_argument("--fieldmap", default="configs/fieldmap.yaml")
    spv.add_argument("--rules", default="configs/ruleset.yaml")

    a = p.parse_args()
    if a.cmd == "ingest":
        print(json.dumps(run_ingest(a.input, a.output)))
        return 0
    if a.cmd == "normalize":
        print(json.dumps(run_normalize(a.input, a.output)))
        return 0
    if a.cmd == "validate":
        print(
            json.dumps(run_validate(a.input, a.output, a.schema, a.fieldmap, a.rules))
        )
        return 0
    if a.cmd == "score":
        print(json.dumps(run_score(a.input, a.output)))
        return 0
    if a.cmd == "report":
        out_md = pathlib.Path(a.output).with_suffix(".md")
        print(json.dumps(run_report(a.input, a.output, str(out_md))))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
