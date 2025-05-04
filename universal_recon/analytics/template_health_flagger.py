"""
Analytics module: template_health_flagger.py
Purpose: Tags each template or record cluster with a basic health classification.
"""


def flag_template_health(records):
    """
    Classifies records or clusters by overall 'health' based on average score and error rate.

    Returns:
        Dict with plugin name, flagged count, and summary.
    """
    if not records:
        return {
            "plugin": "template_health_flagger",
            "flagged": 0,
            "total": 0,
            "summary": [],
        }

    flagged = []
    for record in records:
        score = record.get("score", 0)
        record.get("error")
        severity = record.get("severity", "none")

        if severity == "critical" or score <= 2:
            health = "fragile"
        elif severity == "warning" or score <= 4:
            health = "unstable"
        else:
            health = "healthy"

        flagged.append(
            {
                "type": record.get("type"),
                "value": record.get("value"),
                "plugin": record.get("plugin"),
                "score": score,
                "severity": severity,
                "health": health,
            }
        )

    return {
        "plugin": "template_health_flagger",
        "flagged": len(flagged),
        "total": len(records),
        "summary": flagged,
    }


def run_analysis(records, config=None):
"""TODO: Add docstring."""
    return flag_template_health(records)
