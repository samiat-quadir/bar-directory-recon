def fix_file(file_path):
    """Fix trailing whitespace and ensure file ends with a newline."""
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Fix trailing whitespace
    lines = content.splitlines()
    fixed_lines = [line.rstrip() for line in lines]
    fixed_content = "\n".join(fixed_lines)

    # Ensure file ends with a newline
    if not fixed_content.endswith("\n"):
        fixed_content += "\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"Fixed: {file_path}")


# Files to fix
files_to_fix = ["tools/fix_hardcoded_paths.py", "config/device_config.json"]

# Fix each file
for file in files_to_fix:
    fix_file(file)
