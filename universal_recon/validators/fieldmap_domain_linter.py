# === validators/fieldmap_domain_linter.py ===

import json

def domain_lint_fieldmap(path: str, verbose=False):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    domain_tags = data.get("domain_tags", [])
    fields = data.get("fields", [])
    field_names = {f.get("name") for f in fields if isinstance(f, dict)}

    anomalies = []

    if "bar" in domain_tags and "bar_number" not in field_names:
        anomalies.append("missing_bar_number")

    if "legal" in domain_tags and "email" not in field_names:
        anomalies.append("missing_email_field")

    if anomalies:
        data["anomaly_flags"] = anomalies
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        if verbose:
            print(f"[!] Domain lint anomalies injected into {path}: {anomalies}")
    else:
        if verbose:
            print("[✓] No domain lint issues found.")

    return {"status": "complete", "flags": anomalies}
