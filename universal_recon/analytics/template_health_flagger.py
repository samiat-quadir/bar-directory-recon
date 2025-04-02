# template_health_flagger.py

def run_analysis(records: List[Dict], config: Dict = None) -> Dict:
    """
    Classifies template health by scoring completeness, field presence, and validator severity.
    Returns health category per template block.
    """
    template_health = {}

    for record in records:
        block = record.get("template_block", "default")
        score = record.get("score", 0)
        valid = record.get("valid", True)
        severity = record.get("severity", "info")

        if block not in template_health:
            template_health[block] = {
                "score_sum": 0,
                "count": 0,
                "errors": 0,
            }

        template_health[block]["score_sum"] += score
        template_health[block]["count"] += 1
        if not valid or severity in ["critical", "warning"]:
            template_health[block]["errors"] += 1

    flagged = {}
    for block, stats in template_health.items():
        avg_score = stats["score_sum"] / max(stats["count"], 1)
        error_rate = stats["errors"] / max(stats["count"], 1)

        if error_rate > 0.5 or avg_score < 2:
            label = "fragile"
        elif error_rate > 0.2:
            label = "warning"
        else:
            label = "stable"

        flagged[block] = {
            "avg_score": round(avg_score, 2),
            "error_rate": round(error_rate, 2),
            "health": label
        }

    return {"template_health": flagged}
