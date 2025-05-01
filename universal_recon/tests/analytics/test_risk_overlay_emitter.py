"""Test suite for risk overlay badge generation."""

import json
import os
import tempfile
from unittest import TestCase

import pytest

from universal_recon.analytics.risk_overlay_emitter import (
    calculate_risk_level,
    emit_risk_overlay,
    load_status,
    load_validator_tiers,
)


@pytest.mark.analytics
class TestRiskOverlayEmitter(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Sample matrix data
        self.matrix_data = {
            "utah_bar": {
                "drift_metrics": {"drift_score": 0.7},
                "validators": {"name_parser": {"health": 90}, "email_validator": {"health": 65}},
            }
        }

        # Sample tier definitions
        self.tier_data = {
            "validator_tiers": {
                "critical": {
                    "suppression_factor": 0.80,
                    "badge": "🟥",
                    "description": "Critical validator loss",
                },
                "warning": {
                    "suppression_factor": 0.90,
                    "badge": "🟧",
                    "description": "Moderate validator loss",
                },
                "info": {
                    "suppression_factor": 1.00,
                    "badge": "🟩",
                    "description": "Minor advisory",
                },
            }
        }

        # Create test files
        self.matrix_path = os.path.join(self.temp_dir, "test_matrix.json")
        self.tiers_path = os.path.join(self.temp_dir, "test_tiers.yaml")

        with open(self.matrix_path, "w", encoding="utf-8") as f:
            json.dump(self.matrix_data, f)

        with open(self.tiers_path, "w", encoding="utf-8") as f:
            json.dump(self.tier_data, f)

    def test_calculate_risk_level(self):
        """Test risk level calculation logic."""
        # Test high risk scenarios
        self.assertEqual(
            calculate_risk_level(0.9, 65, 0.8), ("high", "Critical validator issues detected")
        )
        self.assertEqual(
            calculate_risk_level(0.5, 60, 0.9), ("high", "Critical validator issues detected")
        )

        # Test medium risk scenarios
        self.assertEqual(
            calculate_risk_level(0.7, 80, 0.9), ("medium", "Moderate validation concerns")
        )

        # Test low risk scenarios
        self.assertEqual(calculate_risk_level(0.3, 95, 1.0), ("low", "Stable validation state"))

    def test_load_validator_tiers(self):
        """Test loading validator tier definitions."""
        tiers = load_validator_tiers(self.tiers_path)
        self.assertIn("critical", tiers)
        self.assertIn("warning", tiers)
        self.assertIn("info", tiers)
        self.assertEqual(tiers["critical"]["badge"], "🟥")

    def test_emit_risk_overlay(self):
        """Test full risk overlay generation."""
        result = emit_risk_overlay(self.matrix_path, self.tiers_path)

        self.assertIn("risk_badges", result)
        self.assertIn("utah_bar", result["risk_badges"])

        utah_badges = result["risk_badges"]["utah_bar"]
        self.assertIn("name_parser", utah_badges)
        self.assertIn("email_validator", utah_badges)

        # Email validator should be high risk due to health < 70
        self.assertEqual(utah_badges["email_validator"]["risk_level"], "high")
        self.assertEqual(utah_badges["email_validator"]["badge"], "🟥")

        # Name parser should be low/medium risk with 90 health
        self.assertIn(utah_badges["name_parser"]["risk_level"], ["low", "medium"])

    def test_export_json_file(self):
        """Test JSON export functionality."""
        output_path = os.path.join(self.temp_dir, "risk_overlay.json")
        result = emit_risk_overlay(self.matrix_path, self.tiers_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Verify JSON content
        with open(output_path, "r", encoding="utf-8") as f:
            exported = json.load(f)
        self.assertEqual(exported, result)

    def tearDown(self):
        """Clean up temporary test files."""
        for f in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
