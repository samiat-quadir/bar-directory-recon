# universal_recon/analytics/plugin_usage_diff.py

import argparse
import json
import os
from typing import Set

from universal_recon.core.logger import get_logger

logger = get_logger("plugin_diff")


def load_plugins(schema_path: str) -> Set[str]:
    if not os.path.exists(schema_path):
        logger.warning(f"Missing schema: {schema_path}")
        return set()
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            plugins = (
                set(data.get("plugins_used", [])) if isinstance(data, dict) else set()
            )
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in schema: {schema_path}")
        return set()
    return plugins


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare plugin usage between two schema matrices"
    )
    parser.add_argument(
        "--before", required=True, help="Path to the before schema matrix JSON"
    )
    parser.add_argument(
        "--after", required=True, help="Path to the after schema matrix JSON"
    )
    parser.add_argument(
        "--export-json", required=True, help="Path to export diff results JSON"
    )

    args = parser.parse_args()

    plugins_before = load_plugins(args.before)
    plugins_after = load_plugins(args.after)

    missing = plugins_before - plugins_after
    added = plugins_after - plugins_before

    logger.info(f"Missing in after schema: {missing}")
    logger.info(f"Added in after schema: {added}")

    diff_results = {
        "missing_plugins": list(missing),
        "added_plugins": list(added),
        "before_schema": args.before,
        "after_schema": args.after,
    }

    with open(args.export_json, "w", encoding="utf-8") as f:
        json.dump(diff_results, f, indent=2)
    logger.info(f"Diff results exported to {args.export_json}")


if __name__ == "__main__":
    main()
