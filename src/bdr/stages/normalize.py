from __future__ import annotations
from typing import List, Dict, Any


def normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Try to call preserved normalizer; fallback = identity.
    Why: keep demo working without changing runtime if module signature differs."""
    try:
        from universal_recon.utils import record_normalizer as rn  # type: ignore

        # prefer a semantic function if it exists
        for attr in ("normalize_records", "normalize"):
            func = getattr(rn, attr, None)
            if callable(func):
                try:
                    out = func(records)  # type: ignore[call-arg]
                    if isinstance(out, list):
                        return out
                except Exception:
                    pass
    except Exception:
        pass
    return list(records)
