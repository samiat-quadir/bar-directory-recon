# === validators/fieldmap_domain_linter.py ===

import json

    domain_tags = data.get("domain_tags", [])
    fields = data.get("fields", [])
    field_names = {f.get("name") for f in fields if isinstance(f, dict)}

    anomalies = []


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
