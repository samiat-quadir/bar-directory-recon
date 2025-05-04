import json


def check_template_completeness(grouped_profiles, required_fields=None):
    if required_fields is None:
        required_fields = ["name", "email", "firm", "phone"]

    summary = {"full": 0, "partial": 0, "minimal": 0, "total": len(grouped_profiles)}
    annotated = []

    for profile in grouped_profiles:
        present = set([record["type"] for record in profile if record.get("type")])
        matched = [f for f in required_fields if f in present]

        if len(matched) == len(required_fields):
            completeness = "full"
        elif len(matched) >= 2:
            completeness = "partial"
        else:
            completeness = "minimal"

        summary[completeness] += 1
        annotated.append({"completeness": completeness, "records": profile})

    return annotated, summary


def save_checked_template(site_name, annotated_profiles, path="output/templates"):
    out_file = f"{path}/{site_name}_template_checked.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(annotated_profiles, f, indent=2, ensure_ascii=False)
    return out_file
