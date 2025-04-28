# Quick Fieldmap Validation Test
# Runs collect_fieldmap for a mock site and checks output
import os
from universal_recon.analytics.site_schema_collector import collect_fieldmap

def main():
    print("[DEBUG] Starting fieldmap validation test...")
    site = "utah_bar"
    output_path = os.path.join("output", "fieldmap", f"{site}_fieldmap.json")
    print(f"[DEBUG] Calling collect_fieldmap for site: {site}")
    collect_fieldmap(site, verbose=True)
    print(f"[DEBUG] Checking if file exists: {output_path}")
    if os.path.exists(output_path):
        print(f"SUCCESS: {output_path} created.")
    else:
        print(f"FAILURE: {output_path} not found.")

if __name__ == "__main__":
    main()
