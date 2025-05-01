# Quick Validator Drift Detection Test
# Runs validator_drift_overlay.main() and checks output files
import os

from universal_recon.analytics import validator_drift_overlay


def main():
    validator_drift_overlay.main()
    json_path = os.path.join("output", "validator_drift_overlay.json")
    html_path = os.path.join("output", "validator_drift_overlay.html")
    success = True
    if os.path.exists(json_path):
        print(f"SUCCESS: {json_path} exists.")
    else:
        print(f"FAILURE: {json_path} missing.")
        success = False
    if os.path.exists(html_path):
        print(f"SUCCESS: {html_path} exists.")
    else:
        print(f"FAILURE: {html_path} missing.")
        success = False
    # Print drift warnings if any
    if success:
        with open(json_path, "r", encoding="utf-8") as f:
            import json

            data = json.load(f)
            if data.get("drift_warnings"):
                print("Drift warnings detected:")
                for w in data["drift_warnings"]:
                    print(f"- {w}")
            else:
                print("No drift warnings detected.")


if __name__ == "__main__":
    main()
