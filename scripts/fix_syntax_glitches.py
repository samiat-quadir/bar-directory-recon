import pathlib
import re
import sys

ROOT = pathlib.Path(".")
SKIP_DIRS = {".git", ".venv", "venv", ".devcontainer", ".github", "__pycache__"}
PATTERNS = [
    # 1) Duplicate timeout kwarg in requests or subprocess.run calls: timeout=60 appears twice -> keep one
    (
        re.compile(
            r"(requests\.(get|post|put|delete|head|patch)\([^\)]*?),\s*timeout\s*=\s*\d+([^\)]*?),\s*timeout\s*=\s*\d+(\s*\))"
        ),
        r"\1\3\4",
    ),
    (
        re.compile(
            r"(subprocess\.run\([^\)]*?),\s*timeout\s*=\s*\d+([^\)]*?),\s*timeout\s*=\s*\d+(\s*\))"
        ),
        r"\1\2\3",
    ),
    # 2) Stray comma after opening paren in ".split("  (e.g., "command.split(timeout=60)")
    (re.compile(r"\.split\(,\s*"), r".split("),
    # 3) Duplicate keyword pairs like ", timeout=60)
    (
        re.compile(r"(,\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[^,\)]+)(?:(?:,\s*\2\s*=\s*[^,\)]+)+)"),
        lambda m: m.group(1),
    ),
]


def should_skip(p: pathlib.Path) -> bool:
    parts = set(p.parts)
    return any(d in parts for d in SKIP_DIRS)


def fix_text(txt: str) -> str:
    out = txt
    for rx, repl in PATTERNS:
        out = rx.sub(repl, out)
    return out


def main() -> int:
    changed = 0
    for p in ROOT.rglob("*.py"):
        if should_skip(p):
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except Exception:
            continue
        t = fix_text(s)
        if t != s:
            p.write_text(t, encoding="utf-8")
            changed += 1
    print(f"changed_files={changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
