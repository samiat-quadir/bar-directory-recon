# universal_recon/utils/status_summary_emitter.py

import json
from pathlib import Path

import yaml


def load_validation_matrix(yaml_path):
    """
    Load the validation matrix from a YAML file.
    """
    if not Path(yaml_path).exists():
        raise FileNotFoundError(f"Validation matrix file not found: {yaml_path}")
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def emit_status_summary(schema_matrix_path, validation_matrix_path, output_path):
    """
    Generate a status summary based on schema_matrix.json and validation_matrix.yaml.
    """
    # Check if schema_matrix.json exists
    if not Path(schema_matrix_path).exists():
        raise FileNotFoundError(f"Schema matrix file not found: {schema_matrix_path}")

    # Load schema matrix
    with open(schema_matrix_path, "r", encoding="utf-8") as f:
        schema_matrix = json.load(f)

    # Load validation matrix
    validation_matrix = load_validation_matrix(validation_matrix_path)

    # Prepare output summary
    status_summary = {}

    # FIX: iterate over schema_matrix["sites"].items() to match actual structure
    for site, data in schema_matrix.get("sites", {}).items():
        plugins_used = set(data.get("plugins_used", []))
        plugins_removed = []
        validator_drift = False

        for validator, details in validation_matrix.items():
            if details.get("plugin_required", False):
                linked_plugin = details.get("linked_plugin")
                if linked_plugin and linked_plugin not in plugins_used:
                    plugins_removed.append(linked_plugin)
                    validator_drift = True

        status_summary[site] = {
            "validator_drift": validator_drift,
            "plugins_removed": plugins_removed,
            "site_health": "degraded" if validator_drift else "ok",
        }

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write output to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(status_summary, f, indent=2)

    print(f"Status summary written to {output_path}")


def emit_status(matrix_path, export_path, verbose=False):
    """
    Emits a status summary using the provided matrix and export paths.
    Loads output/schema_matrix.json and validators/validation_matrix.yaml,
    writes output/output_status.json, and supports verbose output.
    """
    validation_matrix_path = "universal_recon/validators/validation_matrix.yaml"
    try:
        emit_status_summary(matrix_path, validation_matrix_path, export_path)
        if verbose:
            print(f"emit_status: Status summary generated at {export_path}")
    except Exception as e:
        print(f"emit_status: Error - {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Emit status summary for Universal Recon.")
    parser.add_argument(
        "--matrix_path",
        type=str,
        default="output/schema_matrix.json",
        help="Path to schema_matrix.json",
    )
    parser.add_argument(
        "--export_path",
        type=str,
        default="output/output_status.json",
        help="Path to output status JSON",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    emit_status(args.matrix_path, args.export_path, args.verbose)
