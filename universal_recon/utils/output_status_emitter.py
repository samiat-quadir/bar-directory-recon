import json
import os


def emit_status_json(site_name: str, status_data: dict, output_path: str = "output/output_status.json") -> None:
    """Emit a JSON file with site status for CI/alerting."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    payload = {"site": site_name, "status": status_data}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[✓] Site status exported to: {output_path}")
