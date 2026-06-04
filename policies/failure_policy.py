"""
Empty result failure policy - OPT-IN validation for zero URL/record scenarios.

This module provides configurable validation for empty result sets that would
otherwise pass silently. It supports:
- Allow-empty flags (OPT-IN strict behavior, defaults permit empty)
- Warning thresholds for suspiciously low counts
- Clear error messages with actionable guidance

**Default Behavior (Backward-Compatible)**:
- allow_empty_urls=True → 0 URLs logs warning but continues
- allow_empty_records=True → 0 records logs warning but continues

**Strict Mode (OPT-IN)**:
- allow_empty_urls=False → 0 URLs raises ValueError
- allow_empty_records=False → 0 records raises ValueError
"""

from typing import Optional, List, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FailurePolicy:
    """
    Configuration for empty result validation.
    
    **Defaults are permissive** - strict validation is OPT-IN.
    
    Attributes:
        allow_empty_urls: If False, raises error on 0 URLs (default: True)
        allow_empty_records: If False, raises error on 0 records (default: True)
        url_warning_threshold: Log warning if URL count below this (default: 5)
        record_warning_threshold: Log warning if record count below this (default: 10)
    """
    
    allow_empty_urls: bool = True
    allow_empty_records: bool = True
    url_warning_threshold: int = 5
    record_warning_threshold: int = 10
    
    def __post_init__(self) -> None:
        """Validate threshold values are non-negative."""
        if self.url_warning_threshold < 0:
            raise ValueError("url_warning_threshold must be non-negative")
        if self.record_warning_threshold < 0:
            raise ValueError("record_warning_threshold must be non-negative")


def validate_url_extraction(
    urls: List[str],
    policy: Optional[FailurePolicy] = None,
    context: str = "listing phase"
) -> None:
    """
    Validate URL extraction results against failure policy.
    
    **Default behavior**: Logs warning if 0 URLs but does NOT raise error.
    **Strict mode**: Set policy.allow_empty_urls=False to raise ValueError on empty.
    
    Args:
        urls: List of extracted URLs
        policy: Failure policy config (defaults to permissive settings)
        context: Description of where validation occurred (for error messages)
        
    Raises:
        ValueError: If allow_empty_urls=False and len(urls) == 0
        
    Example:
        >>> # Permissive (default)
        >>> validate_url_extraction([])  # logs warning, continues
        
        >>> # Strict (OPT-IN)
        >>> policy = FailurePolicy(allow_empty_urls=False)
        >>> validate_url_extraction([], policy)  # raises ValueError
    """
    if policy is None:
        policy = FailurePolicy()  # Use permissive defaults
    
    url_count = len(urls)
    
    # Check for empty results
    if url_count == 0:
        message = (
            f"Empty URL extraction during {context}. "
            f"This may indicate: scraping failure, selector changes, or network issues."
        )
        
        if policy.allow_empty_urls:
            logger.warning(message)
        else:
            raise ValueError(
                f"{message}\n"
                f"Validation failed: allow_empty_urls=False. "
                f"Set allow_empty_urls=True to permit empty results."
            )
        return  # Don't check threshold if already at 0
    
    # Check warning threshold
    if url_count < policy.url_warning_threshold:
        logger.warning(
            f"Low URL count during {context}: {url_count} URLs "
            f"(threshold: {policy.url_warning_threshold}). "
            f"Verify scraping logic and selectors."
        )


def validate_record_extraction(
    records: List[Any],
    policy: Optional[FailurePolicy] = None,
    context: str = "detail phase"
) -> None:
    """
    Validate record extraction results against failure policy.
    
    **Default behavior**: Logs warning if 0 records but does NOT raise error.
    **Strict mode**: Set policy.allow_empty_records=False to raise ValueError on empty.
    
    Args:
        records: List of extracted data records
        policy: Failure policy config (defaults to permissive settings)
        context: Description of where validation occurred (for error messages)
        
    Raises:
        ValueError: If allow_empty_records=False and len(records) == 0
        
    Example:
        >>> # Permissive (default)
        >>> validate_record_extraction([])  # logs warning, continues
        
        >>> # Strict (OPT-IN)
        >>> policy = FailurePolicy(allow_empty_records=False)
        >>> validate_record_extraction([], policy)  # raises ValueError
    """
    if policy is None:
        policy = FailurePolicy()  # Use permissive defaults
    
    record_count = len(records)
    
    # Check for empty results
    if record_count == 0:
        message = (
            f"Empty record extraction during {context}. "
            f"This may indicate: parsing failure, schema changes, or invalid data."
        )
        
        if policy.allow_empty_records:
            logger.warning(message)
        else:
            raise ValueError(
                f"{message}\n"
                f"Validation failed: allow_empty_records=False. "
                f"Set allow_empty_records=True to permit empty results."
            )
        return  # Don't check threshold if already at 0
    
    # Check warning threshold
    if record_count < policy.record_warning_threshold:
        logger.warning(
            f"Low record count during {context}: {record_count} records "
            f"(threshold: {policy.record_warning_threshold}). "
            f"Verify parsing logic and data quality."
        )
