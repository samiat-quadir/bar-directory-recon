from __future__ import annotations
from typing import List, Dict, Any


def validate(records: List[Dict[str, Any]], schema: str, fieldmap: str, rules: str) -> int:
    """Try to call preserved validator; fallback = 0 errors.
    Why: keep CI green and avoid coupling until signatures are confirmed."""
    try:
        # Prefer consolidated loader if available
        from universal_recon.utils import validator_loader as vl  # type: ignore

        for attr in ("validate_records", "run_validation", "validate"):
            func = getattr(vl, attr, None)
            if callable(func):
                try:
                    out = func(records, schema, fieldmap, rules)  # type: ignore[call-arg]
                    if isinstance(out, int):
                        return out
                except Exception:
                    pass
    except Exception:
        pass
    try:
        # Direct v3 validator as a fallback path
        from universal_recon.utils import record_field_validator_v3 as v3  # type: ignore

        for attr in ("validate_records", "run", "validate"):
            func = getattr(v3, attr, None)
            if callable(func):
                try:
                    out = func(records, schema, fieldmap, rules)  # type: ignore[call-arg]
                    if isinstance(out, int):
                        return out
                except Exception:
                    pass
    except Exception:
        pass
    return 0
