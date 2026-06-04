# record_normalizer.py
import copy

REQUIRED_FIELDS = ["type", "value", "xpath", "context", "url"]
OPTIONAL_DEFAULTS = {"confidence": 1.0, "source": "unknown", "category": None}


def normalize(records, strict=False, logger=None):
    normalized = []
    for i, record in enumerate(records):
        rec = copy.deepcopy(record)
        missing = [f for f in REQUIRED_FIELDS if f not in rec]
        if missing and strict:
            raise ValueError(f"[Normalizer] Record #{i} missing fields: {missing}")
        for key in OPTIONAL_DEFAULTS:
            rec.setdefault(key, OPTIONAL_DEFAULTS[key])
        if missing and not strict and logger:
            logger(
                f"[Normalizer] Warning: Record #{i} missing required fields {missing}", level="WARN"
            )
        normalized.append(rec)
    return normalized
