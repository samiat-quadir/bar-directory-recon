import os


def clean_merge_conflicts(root="."):
    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(subdir, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "<<<<<<< HEAD" in content:
                    print(f"Cleaning: {path}")
                    cleaned = []
                    skip = False
                    for line in content.splitlines():
                        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
                            skip = not skip
                            continue
                        if not skip:
                            cleaned.append(line)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n".join(cleaned))


if __name__ == "__main__":
    clean_merge_conflicts()
