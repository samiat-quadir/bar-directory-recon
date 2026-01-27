"""
Validation threshold policy - OPT-IN quality score filtering for records.

This module provides configurable validation scoring and filtering:
- Minimum validation score thresholds (OPT-IN strict behavior)
- Separate export of rejected low-quality records
- Detailed validation summary reporting

**Default Behavior (Backward-Compatible)**:
- min_validation_score=0 → No filtering, all records pass
- export_rejected=False → Rejected records are discarded

**Strict Mode (OPT-IN)**:
- min_validation_score > 0 → Filter records below threshold
- export_rejected=True → Export rejected records to separate file
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationPolicy:
    """
    Configuration for validation score filtering.
    
    **Defaults are permissive** - filtering is OPT-IN.
    
    Attributes:
        min_validation_score: Minimum score to pass validation (default: 0 = no filtering)
        export_rejected: Whether to export rejected records to separate file (default: False)
        score_field: Name of field containing validation score (default: 'validation_score')
    """
    
    min_validation_score: float = 0.0
    export_rejected: bool = False
    score_field: str = 'validation_score'
    
    def __post_init__(self) -> None:
        """Validate policy configuration."""
        if self.min_validation_score < 0:
            raise ValueError("min_validation_score must be non-negative")
        if self.min_validation_score > 100:
            raise ValueError("min_validation_score must be <= 100")


def filter_by_validation_score(
    records: List[Dict[str, Any]],
    policy: Optional[ValidationPolicy] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter records by validation score threshold.
    
    **Default behavior**: Returns all records as passed (no filtering).
    **Strict mode**: Set policy.min_validation_score > 0 to enable filtering.
    
    Args:
        records: List of data records (must contain validation score field)
        policy: Validation policy config (defaults to permissive settings)
        
    Returns:
        Tuple of (passed_records, rejected_records)
        
    Example:
        >>> # Permissive (default)
        >>> passed, rejected = filter_by_validation_score(records)
        >>> # All records pass, rejected is empty
        
        >>> # Strict (OPT-IN)
        >>> policy = ValidationPolicy(min_validation_score=60.0)
        >>> passed, rejected = filter_by_validation_score(records, policy)
        >>> # Only records with score >= 60 in passed
    """
    if policy is None:
        policy = ValidationPolicy()  # Use permissive defaults
    
    # If threshold is 0, return all records as passed
    if policy.min_validation_score == 0:
        logger.debug(
            f"Validation filtering disabled (min_validation_score=0). "
            f"Passing all {len(records)} records."
        )
        return records, []
    
    passed_records = []
    rejected_records = []
    
    for record in records:
        score = record.get(policy.score_field, 0.0)
        
        if score >= policy.min_validation_score:
            passed_records.append(record)
        else:
            rejected_records.append(record)
            logger.debug(
                f"Record rejected: score={score} < threshold={policy.min_validation_score}"
            )
    
    logger.info(
        f"Validation filtering: {len(passed_records)} passed, "
        f"{len(rejected_records)} rejected "
        f"(threshold: {policy.min_validation_score})"
    )
    
    return passed_records, rejected_records


def should_export_rejected(policy: Optional[ValidationPolicy] = None) -> bool:
    """
    Check if rejected records should be exported.
    
    Args:
        policy: Validation policy config (defaults to permissive settings)
        
    Returns:
        True if rejected records should be exported to separate file
    """
    if policy is None:
        policy = ValidationPolicy()
    
    return policy.export_rejected
