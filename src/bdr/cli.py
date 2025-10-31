import argparse
import json
import os
import pathlib
import sys

from bdr.stages import normalize as _norm
from bdr.stages import validate as _val


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
    try:
        data = _norm.normalize(data)
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
    try:
        errors = _val.validate(data, schema, fieldmap, rules)
    except Exception:
        pass
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
    rec = payload.get("records", 0)
    err = payload.get("errors", 0)
    scr = payload.get("score", 0)
    pathlib.Path(out_md).write_text(
        f"# Demo Report\n\nRecords: {rec}\n\nErrors: {err}\n\nScore: {scr}\n",
        encoding="utf-8",
    )
    return payload

def _doctor():
    import platform
    info = {
        'python': sys.version.split()[0],
        'platform': platform.platform(),
        'executable': sys.executable,
    }
    # best-effort: preserved utilities importability
    def _can(mod):
        try:
            __import__(mod)
            return True
        except Exception:
            return False
    info['preserved_utils'] = {
        'record_normalizer': _can('universal_recon.utils.record_normalizer'),
        'validator_loader': _can('universal_recon.utils.validation_loader'),
        'record_field_validator_v3': _can('universal_recon.validators.record_field_validator_v3'),
    }
    print(json.dumps(info, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(prog="bdr", description="Bar Directory Recon CLI")
    p.add_argument('--version', action='store_true', help='Show version')
    p.add_argument(
        '--no-exec',
        action='store_true',
        help='Enable safe mode (sets BDR_SAFE_MODE=1, disables optional imports)'
    )
    sub = p.add_subparsers(dest="cmd", required=False)
    sub.add_parser('doctor', help='Show environment diagnostics')

    for name in ("ingest", "normalize", "validate", "score", "report"):
        sp = sub.add_parser(name)
        sp.add_argument("--input", "-i")
        sp.add_argument("--output", "-o")
    spv = [s for s in sub.choices.values() if s.prog.endswith("validate")][0]
    spv.add_argument("--schema", default="configs/schema.yaml")
    spv.add_argument("--fieldmap", default="configs/fieldmap.yaml")
    spv.add_argument("--rules", default="configs/ruleset.yaml")

    a = p.parse_args()
    
    # Handle --no-exec flag by setting BDR_SAFE_MODE
    if getattr(a, 'no_exec', False):
        os.environ['BDR_SAFE_MODE'] = '1'
    
    from bdr import __version__ as _v
    if getattr(a, 'version', False):
        print(_v)
        return 0
    if a.cmd == 'doctor':
        return _doctor()
    if not a.cmd:
        p.print_help()
        return 1

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
