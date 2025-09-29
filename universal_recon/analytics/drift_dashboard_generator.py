"""Drift dashboard generator with integrated risk overlay support."""

import json
import os
from pathlib import Path
from typing import Any, Dict

from universal_recon.analytics.risk_overlay_emitter import emit_risk_overlay

BADGE_COLORS = {
    "ok": "#2ecc71",  # Green
    "degraded": "#f1c40f",  # Yellow/Orange
    "critical": "#e74c3c",  # Red
    "low": "#2ecc71",  # Green for risk levels
    "medium": "#f1c40f",  # Yellow for risk levels
    "high": "#e74c3c",  # Red for risk levels
}


def load_status(status_path: str = "output/output_status.json") -> Dict[str, Any]:
    """Load status data from JSON file."""
    if not os.path.exists(status_path):
        print(f"❌ No status summary found at {status_path}")
        return {}
    with open(status_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_risk_overlay(path: str = "output/risk_overlay.json") -> Dict[str, Any]:
    """Load risk overlay data if available."""
    if not os.path.exists(path):
        return {"risk_badges": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_html(
    status_data: Dict[str, Any],
    risk_data: Dict[str, Any],
    output_path: str = "output/drift_dashboard.html",
) -> None:
    """Generate HTML dashboard with integrated risk overlay."""
    rows = []
    for site, details in status_data.items():
        health = details.get("site_health", "unknown")
        drift = "Yes" if details.get("validator_drift") else "No"
        plugins = (
            ", ".join(details.get("plugins_removed", []))
            if details.get("plugins_removed")
            else "None"
        )
        health_color = BADGE_COLORS.get(health, "#bdc3c7")

        # Add risk overlay badges if available
        risk_badges_html = ""
        site_risks = risk_data.get("risk_badges", {}).get(site, {})
        if site_risks:
            badges = []
            for validator, risk in site_risks.items():
                risk_color = BADGE_COLORS.get(risk["risk_level"], "#bdc3c7")
                badges.append(
                    f'<span title="{risk["description"]}" '
                    f'style="background:{risk_color};padding:2px 6px;border-radius:4px;'
                    f'color:white;margin-right:4px;cursor:help">'
                    f'{risk["badge"]} {validator}</span>'
                )
            risk_badges_html = "".join(badges)

        rows.append(
            f"""
            <tr>
                <td>{site}</td>
                <td><span style="background:{health_color};padding:4px 8px;border-radius:6px;color:white;">{health.upper()}</span></td>
                <td>{drift}</td>
                <td>{plugins}</td>
                <td>{risk_badges_html}</td>
            </tr>
        """
        )

    html = f"""
    <html>
    <head>
        <title>Validator Drift Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; }}
            th {{ background-color: #f5f5f5; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .badge {{ border-radius: 6px; padding: 4px 8px; color: white; }}
        </style>
    </head>
    <body>
        <h1>🛡️ Universal Recon — Drift Dashboard</h1>
        <div style="margin: 1em 0;">
            <p><strong>Legend:</strong></p>
            <p>Health: <span class="badge" style="background:#2ecc71">OK</span>
                       <span class="badge" style="background:#f1c40f">DEGRADED</span>
                       <span class="badge" style="background:#e74c3c">CRITICAL</span></p>
            <p>Risk Levels: 🟩 Low &nbsp; 🟧 Medium &nbsp; 🟥 High</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Health</th>
                    <th>Validator Drift</th>
                    <th>Plugins Removed</th>
                    <th>Risk Overlay</th>
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


def generate_drift_dashboard(matrix_path: str, output_dir: str) -> None:
    """Generate the drift dashboard with risk overlay integration."""
    # Generate risk overlay data first
    validator_tiers_path = str(
        Path(__file__).parent.parent / "validators" / "validator_tiers.yaml"
    )
    risk_data = emit_risk_overlay(matrix_path, validator_tiers_path)

    # Load status and generate dashboard
    status_data = load_status()
    output_path = os.path.join(output_dir, "drift_dashboard.html")
    generate_html(status_data, risk_data, output_path)


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate the Drift Dashboard with risk overlay"
    )
    parser.add_argument(
        "--status-path",
        default="output/output_status.json",
        help="Path to status JSON file",
    )
    parser.add_argument(
        "--matrix-path",
        default="output/schema_matrix.json",
        help="Path to schema matrix JSON",
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

    # Generate risk overlay data
    validator_tiers_path = str(
        Path(__file__).parent.parent / "validators" / "validator_tiers.yaml"
    )
    risk_data = emit_risk_overlay(args.matrix_path, validator_tiers_path)
    generate_html(status_data, risk_data, args.output_path)


if __name__ == "__main__":
    main()
