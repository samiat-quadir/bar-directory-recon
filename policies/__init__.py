"""Package initialization for policies module."""

from .failure_policy import (
    FailurePolicy,
    validate_url_extraction,
    validate_record_extraction,
)

__all__ = [
    'FailurePolicy',
    'validate_url_extraction',
    'validate_record_extraction',
]
