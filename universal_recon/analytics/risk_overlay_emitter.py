"""Risk overlay generation and analysis."""

import json
import os
from typing import Dict, Tuple

from universal_recon.core.logger import get_logger

logger = get_logger(__name__)


def load_validator_tiers(tier_path: str) -> Dict:
    """Load validator tier definitions."""
    try:
        with open(tier_path, "r", encoding="utf-8") as f:
            return json.load(f).get("validator_tiers", {})
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
) -> Dict:
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
