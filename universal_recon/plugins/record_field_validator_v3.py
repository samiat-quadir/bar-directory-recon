# universal_recon/utils/record_field_validator_v3.py

import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["type", "value", "xpath", "context", "url"]
MIN_SCORE_THRESHOLD = 0.6
MIN_TEMPLATE_CONFIDENCE = 0.5


def validate_records(
    records: list[dict], strict: bool = False, verbose: bool = False
) -> list[dict]:
    """
    Validates records using field completeness, score, and predicted score.
    Returns cleaned list (or raises) and logs summary stats.
    """
    passed, failed = [], []

    for rec in records:
        missing = [f for f in REQUIRED_FIELDS if not rec.get(f)]
        score = rec.get("score") or rec.get("predicted_score") or 0
        rec.get("template_confidence") or "medium"

        if missing:
            rec["valid"] = False
            rec["error"] = f"Missing fields: {missing}"
            failed.append(rec)
            if strict:
                raise ValueError(f"Schema violation: {rec['error']}")
            continue

        if score < MIN_SCORE_THRESHOLD:
            rec["valid"] = False
            rec["error"] = f"Score too low ({score})"
            failed.append(rec)
            if strict:
                raise ValueError(f"Scoring violation: {rec['error']}")
            continue

        rec["valid"] = True
        passed.append(rec)

    if verbose or not strict:
        logger.info(f"✅ Validation Complete: {len(passed)} passed, {len(failed)} failed")
        if verbose and failed:
            for f in failed:
                logger.warning(f"[!] Warning: Failed Record: {f.get('error')}")

    return passed
