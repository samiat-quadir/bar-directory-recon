import json
from pathlib import Path

import pytest

from universal_recon.analytics.risk_overlay_emitter import RiskOverlayEmitter


def test_basic_risk(tmp_path):
    # Test validator matrix with critical tier
    test_matrix = {
        "test_validator": {
            "plugin": "test_plugin",
            "on_plugin_removed": "critical",
            "badge_label": "Test Validation",
            "suppression_reason": "Critical validation missing",
            "risk_band": "critical",
        }
    }

    emitter = RiskOverlayEmitter(test_matrix)
    emitter.output_dir = tmp_path
    emitter.emit_risk_overlay()

    # Check JSON output
    json_path = tmp_path / "risk_overlay.json"
    assert json_path.exists()

    with open(json_path) as f:
        result = json.load(f)

    assert "test_validator" in result
    assert result["test_validator"]["risk_level"] == "critical"

    # Check HTML output
    html_path = tmp_path / "risk_overlay.html"
    assert html_path.exists()

    with open(html_path) as f:
        html_content = f.read()

    # Verify HTML contains key elements
    assert "Risk Overlay Report" in html_content
    assert "test_validator" in html_content
    assert 'class="risk-badge critical"' in html_content
    assert "Critical validation missing" in html_content
