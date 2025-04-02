import json
import os

def print_summary_report(summary):
    print("\\n📊 Recon Summary Report")
    print(f"Total Records: {summary.get('total_records')}")
    print(f"Valid Count: {summary.get('valid_count')}")
    print(f"Invalid Count: {summary.get('invalid_count')}")
    print("Top Fields:")
    for field, count in summary.get("top_fields", {}).items():
        print(f"  • {field}: {count}")

def print_audit_report(audit):
    print("\\n🔍 Audit Summary")
    for key, value in audit.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subval in value.items():
                print(f"    • {subkey}: {subval}")
        else:
            print(f"  • {key}: {value}")

def print_trend_report(trend):
    print("\\n📈 Trend Analysis")
    for item in trend.get("field_drift", []):
        print(f"  • {item.get('field')} changed by {item.get('delta')}%")

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def print_full_report(site):
    summary = load_json(f"output/reports/{site}_summary.json")
    audit = load_json(f"output/reports/{site}_audit.json")
    trend = load_json(f"output/reports/{site}_trend.json")

    print_summary_report(summary)
    print_audit_report(audit)
    print_trend_report(trend)