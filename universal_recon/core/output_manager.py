import os
import json

def save_summary(site_name: str, summary: dict):
    """
    Saves the recon summary report as JSON.
    """
    os.makedirs("output/reports", exist_ok=True)
    path = os.path.join("output/reports", f"{site_name}_summary.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[INFO] 🔖 Summary saved to {path}")
