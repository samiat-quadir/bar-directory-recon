import re
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS: list[tuple[re.Pattern[str], str | Callable[[re.Match[str]], str]]] = [
    # Fix malformed subprocess.run calls with missing comma: command.split(), timeout=60
    (
        re.compile(r"command\.split\(\s*,\s*timeout=(\d+)\s*\)"),
        r"command.split(), timeout=\1",
    ),
    # Fix duplicate timeout arguments: timeout=60, ... -> keep first one
    (
        re.compile(r"(.*?timeout\s*=\s*\d+.*?),\s*timeout\s*=\s*\d+"),
        lambda m: m.group(1),
    ),
    # Fix broken subprocess.run with missing parenthesis after split
    (
        re.compile(r"subprocess\.run\(command\.split\(\s*,\s*timeout=(\d+)\),"),
        r"subprocess.run(command.split(), timeout=\1,",
    ),
    # Fix malformed calls with extra comma before timeout
    (
        re.compile(r"subprocess\.run\(([^)]+)\s*,\s*,\s*timeout=(\d+)"),
        r"subprocess.run(\1, timeout=\2",
    ),
    # Remove stray ", timeout=60)" at end of calls
    (re.compile(r",\s*timeout=\d+\s*\)\s*\)"), "))"),
    # Fix duplicate timeout in same function call (any order)
    (
        re.compile(r"(\btimeout\s*=\s*\d+)([^,)]*),([^,)]*)\btimeout\s*=\s*\d+"),
        r"\1\2\3",
    ),
    # Fix Path.cwd with invalid timeout parameter
    (re.compile(r"Path\.cwd\(\s*,\s*timeout=\d+\s*\)"), "Path.cwd()"),
    # Remove extra timeout parameters in various contexts
    (re.compile(r",\s*timeout=\d+\s*,\s*timeout=\d+"), ", timeout=60"),
]


def fix_text(text: str) -> str:
    new_text = text
    for pat, repl in PATTERNS:
        if callable(repl):

            def replacement_func(m: re.Match[str], repl=repl) -> str:
                return repl(m)

            new_text = pat.sub(replacement_func, new_text)
        else:
            new_text = pat.sub(repl, new_text)
    return new_text


def main() -> int:
    py_files = list(ROOT.rglob("*.py"))
    changed = 0
    for f in py_files:
        # Skip .venv but allow .devcontainer, .github, etc.
        if ".venv" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text = fix_text(text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1
            print(f"Fixed: {f.relative_to(ROOT)}")
    print(f"Applied fixes to {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
