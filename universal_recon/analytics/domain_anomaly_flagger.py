# universal_recon/analytics/domain_anomaly_flagger.py

import json
import argparse
from pathlib import Path
from universal_recon.core.logger import get_logger

logger = get_logger(__name__)

def flag_anomalies(matrix_path: str, export_path: str = None, verbose: bool = False):
    matrix = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    updated = False

    for site, data in matrix.get("sites", {}).items():
        anomalies = []

        if "bar" in data.get("domain_tags", []):
            if "bar_number" not in data.get("fields", {}):
                anomalies.append("missing_bar_number")

        if "contact" not in data.get("fields", {}):
            anomalies.append("missing_contact_field")

        if anomalies:
            data["anomaly_flags"] = anomalies
            updated = True
            if verbose:
                logger.warning(f"{site}: {', '.join(anomalies)}")

    if updated and export_path:
        Path(export_path).write_text(json.dumps(matrix, indent=2))
        if verbose:
            logger.info(f"Matrix with anomalies saved to {export_path}")
    elif not updated and verbose:
        logger.info("No anomalies detected.")

def main(args=None):
    parser = argparse.ArgumentParser(description="Domain Anomaly Flagger")
    parser.add_argument("--matrix-path", required=True, help="Path to schema_matrix.json")
    parser.add_argument("--export-json", help="Optional: write modified matrix to this file")
    parser.add_argument("--verbose", action="store_true", help="Verbose printout")
    parsed_args = parser.parse_args(args)

    flag_anomalies(parsed_args.matrix_path, parsed_args.export_json, parsed_args.verbose)

# --- Phase-26 hotfix alias -------------------------------------------
def run_domain_linter(*args, **kwargs):
    """Backward-compat wrapper expected by main.py"""
    if args or kwargs:
        from argparse import Namespace
        return main(Namespace(**kwargs))
    else:
        main()

if __name__ == "__main__":
    main()
