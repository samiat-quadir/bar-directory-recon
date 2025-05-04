# analytics/export_csv_summary.py

import csv
import json
import os
from collections import Counter, defaultdict


def load_matrix(path):
    with open(path) as f:
        return json.load(f)


def write_csv_site_scores(matrix, output_dir):
    path = os.path.join(output_dir, "site_scores.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Site", "Field Score", "Plugin Coverage", "Validation Pass Rate"])
        for site, data in matrix.get("sites", {}).items():
            scores = data.get("score_summary", {})
            writer.writerow(
                [
                    site,
                    scores.get("field_score", ""),
                    scores.get("plugin_coverage", ""),
                    scores.get("validation_pass_rate", ""),
                ]
            )
    print(f"[✓] site_scores.csv written")


def write_csv_plugin_usage(matrix, output_dir):
    path = os.path.join(output_dir, "plugin_usage.csv")
    plugin_counts = Counter()
    domain_plugin_counts = defaultdict(lambda: Counter())

    for site_data in matrix.get("sites", {}).values():
        plugins = site_data.get("plugins_used", [])
        domains = site_data.get("domain_tags", [])
        for plugin in plugins:
            plugin_counts[plugin] += 1
            for domain in domains:
                domain_plugin_counts[domain][plugin] += 1

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain", "Plugin", "Uses"])
        for domain, plugins in domain_plugin_counts.items():
            for plugin, count in plugins.items():
                writer.writerow([domain, plugin, count])
    print(f"[✓] plugin_usage.csv written")


def write_csv_domain_summary(matrix, output_dir):
    path = os.path.join(output_dir, "domain_summary.csv")
    domain_stats = matrix.get("global_stats", {}).get("domain_flag_summary", {})

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain", "Sites", "Avg Field Score"])
        for domain, stats in domain_stats.items():
            writer.writerow([domain, stats["sites"], stats["avg_score"]])
    print(f"[✓] domain_summary.csv written")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Export schema_matrix.json summary to CSVs")
    parser.add_argument(
        "--matrix-path",
        default="output/schema_matrix.json",
        help="Path to schema matrix",
    )
    parser.add_argument("--output-dir", default="output/", help="Output folder for CSVs")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    matrix = load_matrix(args.matrix_path)

    write_csv_site_scores(matrix, args.output_dir)
    write_csv_plugin_usage(matrix, args.output_dir)
    write_csv_domain_summary(matrix, args.output_dir)


if __name__ == "__main__":
    main()
