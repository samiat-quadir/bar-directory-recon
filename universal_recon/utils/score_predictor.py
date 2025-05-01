# utils/score_predictor.py

from typing import Dict, List


def predict_scores(records: List[Dict]) -> List[Dict]:
    """
    Predicts confidence scores for plugin records lacking rank or score.
    Adds:
        - predicted_score: float (0.0 to 1.0)
        - predicted_confidence: str ("low", "medium", "high")
    Preserves existing 'score', 'rank', or 'strongest' if present.
    """

    def basic_heuristic(record: Dict) -> float:
        value = record.get("value", "")
        record_type = record.get("type", "")

        # Length-based scoring
        if len(value) < 3:
            return 0.2
        if len(value) > 100:
            return 0.4

        # Type-based boosts
        if record_type == "email" and "@" in value:
            return 0.9
        elif record_type == "phone" and any(c.isdigit() for c in value):
            return 0.7
        elif record_type == "firm_name":
            return 0.6
        elif record_type == "bar_number":
            return 0.8

        # Fallback
        return 0.5

    def score_to_confidence(score: float) -> str:
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        return "low"

    enhanced_records = []
    for record in records:
        # Preserve existing high-confidence fields
        if any(key in record for key in ("score", "rank", "strongest")):
            enhanced_records.append(record)
            continue

        predicted = basic_heuristic(record)
        record["predicted_score"] = round(predicted, 3)
        record["predicted_confidence"] = score_to_confidence(predicted)
        enhanced_records.append(record)

    return enhanced_records
