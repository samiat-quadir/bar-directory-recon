# === utils/validator_drift_badges.py ===

VALIDATOR_DRIFT_BADGES = {
    "critical": {
        "icon": "❌",
        "css_class": "validator-critical",
        "tooltip": "Critical validator drift – plugin removed",
    },
    "warning": {
        "icon": "⚠️",
        "css_class": "validator-warning",
        "tooltip": "Warning – non-critical plugin drift",
    },
    "info": {"icon": "ℹ️", "css_class": "validator-info", "tooltip": "Informational drift only"},
}
