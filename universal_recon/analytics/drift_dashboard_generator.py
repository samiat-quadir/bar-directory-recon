# universal_recon/analytics/drift_dashboard_generator.py

import json
import os

BADGE_COLORS = {
    "ok": "#2ecc71",  # Green
    "degraded": "#f1c40f",  # Yellow/Orange
    "critical": "#e74c3c",  # Red
}


def load_status(status_path="output/output_status.json"):
    if not os.path.exists(status_path):
        print(f"❌ No status summary found at {status_path}")
        return {}
    with open(status_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_html(status_data, output_path="output/drift_dashboard.html"):
    rows = []
    for site, details in status_data.items():
        health = details.get("site_health", "unknown")
        drift = "Yes" if details.get("validator_drift") else "No"
        plugins = (
            ", ".join(details.get("plugins_removed", []))
            if details.get("plugins_removed")
            else "None"
        )
        color = BADGE_COLORS.get(health, "#bdc3c7")  # default: gray

        rows.append(
            f"""
            <tr>
                <td>{site}</td>
                <td><span style="background:{color};padding:4px 8px;border-radius:6px;color:white;">{health.upper()}</span></td>
                <td>{drift}</td>
                <td>{plugins}</td>
            </tr>
        """
        )

    html = f"""
    <html>
    <head>
        <title>Validator Drift Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .badge {{ border-radius: 6px; padding: 4px 8px; color: white; }}
        </style>
    </head>
    <body>
        <h2>🛡️ Universal Recon — Drift Dashboard</h2>
        <table>
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Health</th>
                    <th>Validator Drift</th>
                    <th>Plugins Removed</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </body>
    </html>
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] Drift Dashboard generated at {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate the Drift Dashboard from site status data"
    )
    parser.add_argument(
        "--status-path",
        default="output/output_status.json",
        help="Path to status JSON file",
    )
    parser.add_argument(
        "--output-path",
        default="output/drift_dashboard.html",
        help="Path to save the drift dashboard HTML",
    )
    args = parser.parse_args()

    status_data = load_status(args.status_path)
    if not status_data:
        print("❌ No data to build dashboard.")
        return
    generate_html(status_data, args.output_path)


if __name__ == "__main__":
    main()
