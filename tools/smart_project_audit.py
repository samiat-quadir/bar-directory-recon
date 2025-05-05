import os
from pathlib import Path


def smart_project_audit(directory: str):
    """Perform a smart audit of the project directory."""
    audit_report = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in [".py", ".yaml", ".json"]:
                audit_report.append(f"Audited: {file_path}")

    report_path = Path("project_audit_report.txt")
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(audit_report))

    print(f"Audit report saved to {report_path}")


if __name__ == "__main__":
    smart_project_audit(".")
