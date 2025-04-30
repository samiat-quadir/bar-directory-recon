# universal_recon/analytics/plugin_usage_diff.py

import json
import os
from universal_recon.core.logger import get_logger

logger = get_logger("plugin_diff")

def load_plugins(site_fieldmap_path):
    if not os.path.exists(site_fieldmap_path):
        logger.warning(f"Missing fieldmap: {site_fieldmap_path}")
        return set()
    with open(site_fieldmap_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        plugins = set(data.get("plugins_used", [])) if isinstance(data, dict) else set()
    return plugins

def main():
    site1 = "utah_bar"
    site2 = "arizona_bar"
    plugins1 = load_plugins(f"output/fieldmap/{site1}_fieldmap.json")
    plugins2 = load_plugins(f"output/fieldmap/{site2}_fieldmap.json")

    missing = plugins1 - plugins2
    added = plugins2 - plugins1

    logger.info(f"{site2} missing: {missing}")
    logger.info(f"{site2} added: {added}")

if __name__ == "__main__":
    main()
