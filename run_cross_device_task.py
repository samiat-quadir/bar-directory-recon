import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import yaml

CFG = yaml.safe_load(
    Path("automation/cross_device_tasks.yaml").read_text(encoding="utf-8")
)


def ensure_identity_opts(cmd: str) -> str:
    for proto in ("ssh ", "scp "):
        if proto in cmd and "-o IdentitiesOnly=" not in cmd:
            cmd = cmd.replace(proto, f"{proto}-o IdentitiesOnly=yes ", 1)
        if proto in cmd and "-o ServerAliveInterval=" not in cmd:
            cmd = cmd.replace(
                proto,
                f"{proto}-o ServerAliveInterval=30 -o ServerAliveCountMax=4 -o ConnectTimeout=10 ",
                1,
            )
    return cmd


def maybe_local_fastpath(cmd: str) -> str | None:
    me = os.environ.get("COMPUTERNAME", "").upper()
    if me == "MOTHERSHIP" and cmd.strip().startswith("ssh ") and " mothership " in cmd:
        payload = cmd.split('"', 2)[1] if '"' in cmd else None
        return payload
    if me == "ROG-LUCCI" and cmd.strip().startswith("ssh ") and " rog-lucci " in cmd:
        payload = cmd.split('"', 2)[1] if '"' in cmd else None
        return payload
    return None


def run_one(name, cmd, verbose=False, timeout=None, identity_file=None):
    cmd = ensure_identity_opts(cmd)
    if identity_file and ("ssh " in cmd or "scp " in cmd) and " -i " not in cmd:
        parts = cmd.split(" ", 1)
        cmd = parts[0] + f" -i {identity_file} " + parts[1]
    local = maybe_local_fastpath(cmd)
    real = local or cmd
    if verbose:
        print("[RUN]", name, "=>", real)
    try:
        cp = subprocess.run(real, shell=True, timeout=timeout)
        return cp.returncode
    except subprocess.TimeoutExpired:
        print("[TIMEOUT]", name)
        return 124


ap = argparse.ArgumentParser(description="Cross-device task/workflow runner")
ap.add_argument("target", nargs="?", help="task or workflow name")
ap.add_argument("--list", action="store_true", help="List tasks")
ap.add_argument("--list-workflows", action="store_true", help="List workflows")
ap.add_argument("--dry-run", action="store_true", help="Show commands only")
ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
ap.add_argument("--json", action="store_true", help="Emit JSON summary")
ap.add_argument("--timeout", type=int, default=None, help="Per-command timeout")
ap.add_argument("--retries", type=int, default=0, help="Retries for failures")
ap.add_argument("--retry-delay", type=int, default=3, help="Seconds between retries")
ap.add_argument("--identity-file", default=None, help="Explicit SSH identity file")
ap.add_argument("--log-file", dest="log_file", default=None, help="Append plain-text log output to this file")
args = ap.parse_args()


def _log(line: str, *, lf_path: Optional[str]):
    print(line)
    if not lf_path:
        return
    try:
        log_path = Path(lf_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        # best-effort logging
        pass

tasks = CFG.get("tasks", {})
flows = CFG.get("workflows", {})
if args.list:
    print("Tasks:", ", ".join(sorted(tasks.keys())))
    sys.exit(0)
if args.list_workflows:
    print("Workflows:", ", ".join(sorted(flows.keys())))
    sys.exit(0)
if not args.target:
    print(
        "Usage: python run_cross_device_task.py <task|workflow> [--list --list-workflows]"
    )
    sys.exit(1)

items = []
if args.target in tasks:
    items = [args.target]
elif args.target in flows:
    items = flows[args.target]
else:
    print("Unknown target:", args.target)
    sys.exit(2)

results = []
for name in items:
    cmd = tasks[name]["command"]
    if args.dry_run:
        _log(f"[DRY-RUN] {name} => {ensure_identity_opts(cmd)}", lf_path=args.log_file)
        rc = 0
    else:
        attempts = args.retries + 1
        rc = 1  # pessimistic default
        for i in range(attempts):
            _log(f"[EXEC] {name} attempt {i+1}/{attempts}", lf_path=args.log_file)
            rc = run_one(
                name,
                cmd,
                verbose=args.verbose,
                timeout=args.timeout,
                identity_file=args.identity_file,
            )
            if rc == 0:
                _log(f"[OK] {name}", lf_path=args.log_file)
                break
            if i < attempts - 1:
                _log(
                    f"[RETRY] {name} rc={rc}, sleeping {args.retry_delay}s…",
                    lf_path=args.log_file,
                )
                time.sleep(args.retry_delay)
            else:
                _log(f"[FAIL] {name} rc={rc}", lf_path=args.log_file)
    results.append((name, rc))
if args.json:
    summary = {"results": [{"name": n, "rc": rc} for n, rc in results]}
    _log(json.dumps(summary, indent=2), lf_path=args.log_file)
    if not args.log_file:  # already printed if log_file present
        pass

# exit non-zero if any failed
sys.exit(max(rc for _, rc in results))
