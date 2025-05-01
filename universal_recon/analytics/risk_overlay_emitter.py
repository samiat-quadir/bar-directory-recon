"""Risk overlay badge generator for validator drift analysis.

Added in Phase 27 to support risk-based validation overlay badges.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml


class RiskOverlayEmitter:
    def __init__(self, validator_matrix: Dict[str, Any]):
        self.validator_matrix = validator_matrix
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def _calculate_risk_level(self, validator_data: Dict[str, Any]) -> str:
        """Calculate risk level based on validator data and suppression factor."""
        risk_band = validator_data.get("risk_band", "low")

        # Map risk bands to numeric values
        risk_levels = {"critical": 3, "high": 2, "medium": 1, "low": 0}

        base_risk = risk_levels.get(risk_band, 0)

        # Apply suppression factor if validator is removed
        if validator_data.get("on_plugin_removed") == "critical":
            return "critical"

        return risk_band

    def _generate_html(self, risk_data: Dict[str, Any]) -> str:
        """Generate HTML representation of risk overlay data."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Risk Overlay Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .risk-badge {
                    padding: 5px 10px;
                    border-radius: 4px;
                    margin: 5px 0;
                    display: inline-block;
                }
                .critical { background-color: #ff4444; color: white; }
                .high { background-color: #ffa500; color: white; }
                .medium { background-color: #ffff00; color: black; }
                .low { background-color: #00ff00; color: black; }
                .validator-item {
                    border: 1px solid #ddd;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <h1>Risk Overlay Report</h1>
            <div class="validators">
        """

        for validator_name, data in risk_data.items():
            html_template += f"""
                <div class="validator-item">
                    <h3>{validator_name}</h3>
                    <span class="risk-badge {data['risk_level']}">{data['risk_level'].upper()}</span>
                    <p><strong>Badge Label:</strong> {data['badge_label']}</p>
                    <p><strong>Suppression Reason:</strong> {data['suppression_reason']}</p>
                </div>
            """

        html_template += """
            </div>
        </body>
        </html>
        """
        return html_template

    def emit_risk_overlay(self) -> None:
        """Generate and save risk overlay data to both JSON and HTML files."""
        risk_data = {
            validator_name: {
                "risk_level": self._calculate_risk_level(validator_data),
                "suppression_reason": validator_data.get("suppression_reason", ""),
                "badge_label": validator_data.get("badge_label", ""),
            }
            for validator_name, validator_data in self.validator_matrix.items()
        }

        # Save JSON output
        json_path = self.output_dir / "risk_overlay.json"
        with open(json_path, "w") as f:
            json.dump(risk_data, f, indent=2)

        # Save HTML output
        html_path = self.output_dir / "risk_overlay.html"
        with open(html_path, "w") as f:
            f.write(self._generate_html(risk_data))
