"""Risk overlay generation and analysis."""

import json
import os
from typing import Any, Dict, Tuple

from universal_recon.core.logger import get_logger

logger = get_logger(__name__)


def load_validator_tiers(tier_path: str) -> Dict[str, Any]:
    """Load validator tier definitions."""
    try:
        with open(tier_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("validator_tiers", {}) if isinstance(data, dict) else {}
    except Exception as e:
        logger.error(f"Error loading validator tiers: {e}")
        return {}


def calculate_risk_level(
    drift_score: float, health: float, suppression_factor: float
) -> Tuple[str, str]:
    """Calculate risk level based on metrics."""
    if drift_score > 0.8 or health < 70 * suppression_factor:
        return ("high", "Critical validator issues detected")
    elif drift_score > 0.6 or health < 85 * suppression_factor:
        return ("medium", "Moderate validation concerns")
    return ("low", "Stable validation state")


def emit_site_risk_json(
    site_name: str, drift_score: float, health: float, suppression_factor: float, tier_path: str
) -> Dict[str, Any]:
    """Generate risk overlay JSON for a site."""
    try:
        validator_tiers = load_validator_tiers(tier_path)
        if not validator_tiers:
            raise ValueError("Validator tiers could not be loaded")

        risk_level, message = calculate_risk_level(drift_score, health, suppression_factor)
        return {
            "site": site_name,
            "risk_level": risk_level,
            "message": message,
            "validator_tiers": validator_tiers,
        }
    except Exception as e:
        logger.error(f"Error generating risk overlay: {e}")
        return {"site": site_name, "risk_level": "error", "message": str(e)}


def emit_risk_overlay(matrix_path: str, validator_tiers_path: str) -> Dict[str, Any]:
    """Generate risk overlay data from matrix and validator tiers."""
    try:
        # Load validator tiers
        validator_tiers = load_validator_tiers(validator_tiers_path)
        if not validator_tiers:
            logger.warning("No validator tiers loaded, using defaults")
            return {"risk_badges": {}}

        # Load matrix data
        try:
            with open(matrix_path, "r", encoding="utf-8") as f:
                matrix_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading matrix data: {e}")
            return {"risk_badges": {}}

        # Generate risk badges for each site and validator
        risk_badges = {}
        for site_name, site_data in matrix_data.items():
            if not isinstance(site_data, dict):
                continue

            validators = site_data.get("validators", {})
            drift_metrics = site_data.get("drift_metrics", {})
            drift_score = drift_metrics.get("drift_score", 0.0)

            site_badges = {}
            for validator_name, validator_data in validators.items():
                if not isinstance(validator_data, dict):
                    continue

                health = validator_data.get("health", 100.0)

                # Calculate risk level for this validator
                risk_level, message = calculate_risk_level(drift_score, health, 1.0)

                # Find appropriate badge from validator tiers
                badge = "🟩"  # Default
                for tier_name, tier_data in validator_tiers.items():
                    if tier_data.get("suppression_factor", 1.0) <= 1.0:
                        if risk_level == "high" and tier_name == "critical":
                            badge = tier_data.get("badge", "🟥")
                        elif risk_level == "medium" and tier_name == "warning":
                            badge = tier_data.get("badge", "🟧")
                        elif risk_level == "low" and tier_name == "info":
                            badge = tier_data.get("badge", "🟩")

                site_badges[validator_name] = {
                    "risk_level": risk_level,
                    "message": message,
                    "badge": badge,
                    "health": health
                }

            risk_badges[site_name] = site_badges

        result = {"risk_badges": risk_badges}

        # Export to JSON file (same directory as matrix)
        output_dir = os.path.dirname(matrix_path)
        output_path = os.path.join(output_dir, "risk_overlay.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result

    except Exception as e:
        logger.error(f"Error generating risk overlay: {e}")
        return {"risk_badges": {}}
