"""Utility to run predefined cross-device tasks.

Enhancements over original minimal version:
 - Argparse interface (list tasks, dry-run, verbose)
 - Ensures IdentitiesOnly for ssh/scp commands
 - Optional retry with -vvv for SSH auth diagnostics
 - Streams output and returns non-zero on failure without stack trace noise
 - Provides guidance if Permission denied (publickey) occurs
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

import yaml

TASKS_FILE = Path("automation/cross_device_tasks.yaml")


def load_tasks() -> Dict[str, Any]:
    if not TASKS_FILE.exists():
        print(f"[ERROR] Tasks file not found: {TASKS_FILE}")
        sys.exit(2)
    try:
        cfg = yaml.safe_load(TASKS_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print("[ERROR] Failed to parse YAML:", e)
        sys.exit(2)
    return cfg.get("tasks", {})


KEEPALIVE_OPTS = [
    "-o", "IdentitiesOnly=yes",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=4",
    "-o", "ConnectTimeout=10",
    "-o", "Compression=yes",
]


def normalize_command(raw: str, identity_file: str | None = None) -> str:
    cmd = raw.strip()
    if cmd.startswith("ssh "):
        # If user already provided any of our keepalive flags, skip injecting duplicates.
        if not any(flag in cmd for flag in ["ServerAliveInterval", "ServerAliveCountMax", "ConnectTimeout"]):
            # Use simple string replacement to avoid shlex issues with Windows escaping
            rest = cmd[4:]  # Everything after "ssh "
            opts_str = " ".join(KEEPALIVE_OPTS)
            cmd = f"ssh {opts_str} {rest}"
        elif "IdentitiesOnly" not in cmd:
            cmd = cmd.replace("ssh ", "ssh -o IdentitiesOnly=yes ", 1)

        # Inject identity file if specified and not already present
        if identity_file and " -i " not in cmd:
            # Insert -i option after ssh and existing options but before hostname
            parts = cmd.split(" ", 1)
            if len(parts) == 2:
                ssh_part = parts[0]  # "ssh"
                rest_part = parts[1]  # everything else
                # Find where hostname starts (after all -o options)
                tokens = rest_part.split()
                insert_pos = 0
                for i, token in enumerate(tokens):
                    if token.startswith("-o") or token.startswith("-i") or token.startswith("-v"):
                        if token == "-o" and i + 1 < len(tokens):
                            insert_pos = i + 2  # Skip -o and its value
                        else:
                            insert_pos = i + 1
                    else:
                        break
                tokens.insert(insert_pos, "-i")
                tokens.insert(insert_pos + 1, identity_file)
                cmd = f"{ssh_part} {' '.join(tokens)}"

    elif cmd.startswith("scp "):
        if "IdentitiesOnly" not in cmd:
            rest = cmd[4:]  # Everything after "scp "
            cmd = f"scp -o IdentitiesOnly=yes {rest}"

        # Inject identity file for scp as well
        if identity_file and " -i " not in cmd:
            parts = cmd.split(" ", 1)
            if len(parts) == 2:
                scp_part = parts[0]  # "scp"
                rest_part = parts[1]  # everything else
                tokens = rest_part.split()
                insert_pos = 0
                for i, token in enumerate(tokens):
                    if token.startswith("-o") or token.startswith("-i"):
                        if token == "-o" and i + 1 < len(tokens):
                            insert_pos = i + 2
                        else:
                            insert_pos = i + 1
                    else:
                        break
                tokens.insert(insert_pos, "-i")
                tokens.insert(insert_pos + 1, identity_file)
                cmd = f"{scp_part} {' '.join(tokens)}"
    return cmd


def run_command(
    cmd: str,
    retry_verbose: bool = False,
    timeout: int | None = None,
    capture: bool = False,
) -> tuple[int, str, str, float]:
    start = time.time()
    print(f"[INFO] Executing: {cmd}")
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        return 124, "", "[TIMEOUT] Command exceeded timeout", time.time() - start
    rc = proc.returncode
    if rc != 0 and retry_verbose and cmd.startswith("ssh ") and " -vvv " not in cmd:
        print("[WARN] Command failed. Retrying with SSH verbose (-vvv) for diagnostics...")
        verbose_cmd = cmd.replace("ssh ", "ssh -vvv ", 1)
        v_proc = subprocess.Popen(
            verbose_cmd,
            shell=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
        )
        v_out, v_err = v_proc.communicate()
        stdout = (stdout or "") + ("\n" + v_out if v_out else "")
        stderr = (stderr or "") + ("\n" + v_err if v_err else "")
        rc = v_proc.returncode
    if rc == 255 and "ssh" in cmd and stderr is not None:
        stderr += (
            "\n[HINT] SSH return code 255 often indicates auth/network issues.\n"
            "Verify key in remote authorized_keys; test: ssh -o IdentitiesOnly=yes <host> 'echo ok'\n"
            "Use --retry-verbose for negotiation logs."
        )
    return rc, stdout or "", stderr or "", time.time() - start


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run cross-device automation tasks")
    parser.add_argument("task", nargs="?", help="Task name to run (omit with --list)")
    parser.add_argument("--list", action="store_true", help="List available tasks")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--retry-verbose", action="store_true", help="Retry failing SSH with -vvv")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON result")
    parser.add_argument("--timeout", type=int, help="Timeout (seconds) for command execution")
    parser.add_argument("--verbose", action="store_true", help="Verbose diagnostics (does not imply SSH -vvv)")
    parser.add_argument("--identity-file", type=str, help="Override SSH identity file (path to private key)")
    args = parser.parse_args(argv)

    tasks = load_tasks()
    if args.list:
        print("Available tasks:")
        for name in sorted(tasks):
            print(" -", name)
        return 0
    if not args.task:
        parser.print_help()
        return 1
    if args.task not in tasks:
        print(f"[ERROR] Unknown task '{args.task}'. Use --list to view tasks.")
        return 1
    raw_cmd = tasks[args.task]["command"]

    # Fast-path: If command targets self via ssh (rog-lucci) and we are on that host, execute locally.
    hostname = os.environ.get("COMPUTERNAME", "").lower()
    if hostname and "rog-lucci" in hostname and raw_cmd.startswith("ssh rog-lucci "):
        # Extract inner remote command (after first space following host)
        try:
            # More careful parsing to preserve Windows command structure
            parts = raw_cmd.split(" ", 2)
            if len(parts) >= 3:
                inner = parts[2]
                # Remove outer quotes but preserve inner structure
                if inner.startswith('"') and inner.endswith('"'):
                    inner = inner[1:-1]
                # For Windows cmd commands, ensure proper escaping is preserved
                raw_cmd = inner.replace('^"', '"').replace('^^', '^')
                if args.verbose:
                    print(f"[FAST-PATH] Executing task locally: {raw_cmd}")
        except (IndexError, AttributeError):
            pass

    cmd = normalize_command(raw_cmd, args.identity_file)
    if args.dry_run:
        print(f"[DRY-RUN] {cmd}")
        return 0
    rc, out, err, elapsed = run_command(
        cmd,
        retry_verbose=args.retry_verbose,
        timeout=args.timeout,
        capture=args.json,
    )
    if args.json:
        payload = {
            "task": args.task,
            "command": cmd,
            "return_code": rc,
            "elapsed_sec": round(elapsed, 3),
            "stdout": out,
            "stderr": err,
            "host": hostname,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        print(json.dumps(payload, indent=2))
    else:
        if out:
            print(out.rstrip())
        if err:
            print(err.rstrip())
        if rc == 0:
            print(f"[SUCCESS] Task completed in {elapsed:.2f}s.")
        else:
            print(f"[FAIL] Task exited with code {rc} after {elapsed:.2f}s.")
    return rc


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
