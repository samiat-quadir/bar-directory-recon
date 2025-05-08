import subprocess

TARGET_DIR = "."
# Exclude virtual environments and build artifacts
EXCLUDE_PATTERN = r"\.venv311|\.venv|build|dist"

commands = [
    ("Black", ["black", "--exclude", EXCLUDE_PATTERN, TARGET_DIR]),
    ("Isort", ["isort", TARGET_DIR]),
    ("Ruff", ["ruff", "--fix", TARGET_DIR]),
    (
        "Autoflake",
        [
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            "--recursive",
            TARGET_DIR,
            "--exclude",
            EXCLUDE_PATTERN,
        ],
    ),
]


def run_linter(name, cmd):
    print(f"\n🔍 Running {name}...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"✅ {name} passed.")
    else:
        print(f"❌ {name} failed.")


if __name__ == "__main__":
    for name, cmd in commands:
        run_linter(name, cmd)
