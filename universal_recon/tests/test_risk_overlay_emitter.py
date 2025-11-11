import json
import os
import tempfile
from pathlib import Path

import pytest

from universal_recon.analytics.risk_overlay_emitter import (
    calculate_risk_level,
    emit_site_risk_json,
    load_validator_tiers,
)


def test_emit_site_risk_json(tmp_path):
    """Test emit_site_risk_json function with mock inputs."""
    # Create a temporary test tier file
    tier_path = tmp_path / "test_tiers.json"
    test_tiers = {
        "validator_tiers": {
            "critical": {"badge": "🟥", "color": "#e74c3c", "suppression_factor": 0.8},
            "warning": {"badge": "🟧", "color": "#f39c12", "suppression_factor": 0.9},
            "info": {"badge": "🟩", "color": "#2ecc71", "suppression_factor": 1.0},
        }
    }

    with open(tier_path, "w", encoding="utf-8") as f:
        json.dump(test_tiers, f)

    # Test high risk scenario
    high_risk_result = emit_site_risk_json(
        site_name="test_site_high",
        drift_score=0.85,
        health=65,
        suppression_factor=0.9,
        tier_path=str(tier_path),
    )

    assert high_risk_result["site"] == "test_site_high"
    assert high_risk_result["risk_level"] == "high"
    assert high_risk_result["message"] == "Critical validator issues detected"
    assert "validator_tiers" in high_risk_result

    # Test medium risk scenario
    medium_risk_result = emit_site_risk_json(
        site_name="test_site_medium",
        drift_score=0.7,
        health=80,
        suppression_factor=0.9,
        tier_path=str(tier_path),
    )

    assert medium_risk_result["site"] == "test_site_medium"
    assert medium_risk_result["risk_level"] == "medium"
    assert medium_risk_result["message"] == "Moderate validation concerns"

    # Test low risk scenario
    low_risk_result = emit_site_risk_json(
        site_name="test_site_low",
        drift_score=0.3,
        health=95,
        suppression_factor=1.0,
        tier_path=str(tier_path),
    )

    assert low_risk_result["site"] == "test_site_low"
    assert low_risk_result["risk_level"] == "low"
    assert low_risk_result["message"] == "Stable validation state"


def test_calculate_risk_level():
    """Test risk level calculation."""
    # Test high risk scenarios
    assert calculate_risk_level(0.85, 65, 0.9) == ("high", "Critical validator issues detected")
    assert calculate_risk_level(0.5, 60, 0.9) == ("high", "Critical validator issues detected")

    # Test medium risk scenarios
    assert calculate_risk_level(0.7, 80, 0.9) == ("medium", "Moderate validation concerns")
    assert calculate_risk_level(0.5, 80, 0.9) == ("low", "Stable validation state")

    # Test low risk scenarios
    assert calculate_risk_level(0.3, 95, 1.0) == ("low", "Stable validation state")


def test_load_validator_tiers(tmp_path):
    """Test loading validator tier definitions."""
    tier_path = tmp_path / "test_tiers.json"
    test_tiers = {
        "validator_tiers": {
            "critical": {"badge": "🟥", "color": "#e74c3c"},
            "warning": {"badge": "🟧", "color": "#f39c12"},
            "info": {"badge": "🟩", "color": "#2ecc71"},
        }
    }

    with open(tier_path, "w", encoding="utf-8") as f:
        json.dump(test_tiers, f)

    tiers = load_validator_tiers(str(tier_path))
    assert "critical" in tiers
    assert "warning" in tiers
    assert "info" in tiers
    assert tiers["critical"]["badge"] == "🟥"
    assert tiers["warning"]["badge"] == "🟧"
    assert tiers["info"]["badge"] == "🟩"
