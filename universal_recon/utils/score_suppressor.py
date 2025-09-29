# === universal_recon/utils/score_suppressor.py ===

import json
import os


def suppress_scores(
    matrix_path="output/schema_matrix.json",
    status_path="output/output_status.json",
    export_path="output/schema_matrix_suppressed.json",
    suppress_factor=0.9,
    verbose=False,
):
    if not os.path.exists(matrix_path) or not os.path.exists(status_path):
        print("❌ Required input files not found.")
        return

    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)

    with open(status_path, "r", encoding="utf-8") as f:
        status = json.load(f)

    modified_sites = 0
    for site, data in matrix.get("sites", {}).items():
        site_status = status.get(site, {})
        if site_status.get("site_health") == "degraded":
            score = data.get("score_summary", {}).get("field_score")
            if isinstance(score, (int, float)):
                suppressed_score = round(score * suppress_factor, 2)
                matrix["sites"][site]["score_summary"]["field_score"] = suppressed_score
                if verbose:
                    print(f"[!] Suppressed {site} score: {score} → {suppressed_score}")
                modified_sites += 1

    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)

    print(f"[✓] Score-suppressed matrix written to: {export_path}")
    print(f"[•] {modified_sites} site(s) suppressed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Suppress schema scores based on drift risk"
    )
    parser.add_argument("--matrix-path", default="output/schema_matrix.json")
    parser.add_argument("--status-path", default="output/output_status.json")
    parser.add_argument("--export-path", default="output/schema_matrix_suppressed.json")
    parser.add_argument("--suppress-factor", type=float, default=0.9)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    suppress_scores(
        matrix_path=args.matrix_path,
        status_path=args.status_path,
        export_path=args.export_path,
        suppress_factor=args.suppress_factor,
        verbose=args.verbose,
    )
