import json
import subprocess
import sys
from pathlib import Path
Q = Path("automation/queue"); Q.mkdir(parents=True, exist_ok=True)
RUNNER = [sys.executable, "run_cross_device_task.py"]
def run_task(name, args): return subprocess.run(RUNNER + [name] + args, shell=False).returncode
def main():
    for jf in sorted(Q.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        name = data["target"]; args = data.get("args", [])
        print(f"[QUEUE] {jf.name} -> {name} {args}")
        rc = run_task(name, args); print(f"[QUEUE] rc={rc}")
        jf.rename(jf.with_suffix(".done.json") if rc == 0 else jf.with_suffix(".fail.json"))
if __name__ == "__main__": main()
