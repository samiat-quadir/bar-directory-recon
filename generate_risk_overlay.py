from universal_recon.analytics.risk_overlay_emitter import RiskOverlayEmitter

test_matrix = {
    "email_validator": {
        "plugin": "email_plugin",
        "on_plugin_removed": "warning",
        "badge_label": "Email Validation",
        "suppression_reason": "Missing email validation reduces contactability",
        "risk_band": "medium",
    },
    "bar_number_check": {
        "plugin": "bar_number_annotator",
        "on_plugin_removed": "critical",
        "badge_label": "Bar Number Check",
        "suppression_reason": "Missing bar number verification",
        "risk_band": "critical",
    },
}

emitter = RiskOverlayEmitter(test_matrix)
emitter.emit_risk_overlay()
