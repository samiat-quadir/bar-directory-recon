# utils/score_predictor.py

"""Score prediction for validation records."""
from typing import Dict, List, Union

from universal_recon.core.logger import get_logger

logger = get_logger(__name__)


def predict_score(records: List[Dict]) -> List[Dict]:
    """Predict validation scores for records."""
    try:
        predictions = []
        for record in records:
            value = record.get("value", "")
            record_type = record.get("type", "")

            # Basic heuristic scoring
            score = 0.0
            confidence = "low"

            if record_type == "email":
                score = 0.9 if "@" in value and "." in value else 0.2
                confidence = "high" if "@" in value else "low"
            elif record_type == "phone":
                score = 0.8 if len(value) >= 7 else 0.3
                confidence = "medium"
            else:
                score = 0.7 if len(value) > 3 else 0.4
                confidence = "medium"

            prediction = record.copy()
            prediction["predicted_score"] = score
            prediction["predicted_confidence"] = confidence
            predictions.append(prediction)

        return predictions
    except Exception as e:
        logger.error(f"Error predicting scores: {e}")
        return records
