"""
Validation summary and scoring - comprehensive tracking of validation results.

Provides detailed statistics on validation pass/fail rates, reasons for failures,
and summary reporting for audit and debugging.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationSummary:
    """
    Track and summarize validation results across a dataset.
    
    Maintains counters for:
    - Total records processed
    - Records that passed validation
    - Records that failed validation
    - Breakdown of failure reasons
    
    Attributes:
        total_records: Total number of records validated
        passed_validation: Number of records that passed
        failed_validation: Number of records that failed
        validation_rate: Percentage of records that passed (0-100)
        failures_by_reason: Count of failures by reason code
    """
    
    total_records: int = 0
    passed_validation: int = 0
    failed_validation: int = 0
    validation_rate: float = 0.0
    failures_by_reason: Dict[str, int] = field(default_factory=dict)
    
    def add_validation_result(self, passed: bool, reason: Optional[str] = None) -> None:
        """
        Record the result of validating a single record.
        
        Args:
            passed: Whether the record passed validation
            reason: If failed, the reason code for failure (e.g., 'low_score', 'missing_field')
        """
        self.total_records += 1
        
        if passed:
            self.passed_validation += 1
        else:
            self.failed_validation += 1
            if reason:
                self.failures_by_reason[reason] = self.failures_by_reason.get(reason, 0) + 1
        
        # Recalculate validation rate
        if self.total_records > 0:
            self.validation_rate = (self.passed_validation / self.total_records) * 100
    
    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get validation summary as a dictionary for export.
        
        Returns:
            Dictionary with validation statistics and failure breakdown
        """
        return {
            'total_records': self.total_records,
            'passed_validation': self.passed_validation,
            'failed_validation': self.failed_validation,
            'validation_rate_percent': round(self.validation_rate, 2),
            'failures_by_reason': self.failures_by_reason,
        }
    
    def log_summary(self) -> None:
        """Log validation summary to logger."""
        logger.info(
            f"Validation Summary: {self.passed_validation}/{self.total_records} passed "
            f"({self.validation_rate:.1f}%), {self.failed_validation} failed"
        )
        
        if self.failures_by_reason:
            logger.info("Failure breakdown:")
            for reason, count in sorted(self.failures_by_reason.items(), key=lambda x: -x[1]):
                logger.info(f"  - {reason}: {count}")
    
    def reset(self) -> None:
        """Reset all counters to zero."""
        self.total_records = 0
        self.passed_validation = 0
        self.failed_validation = 0
        self.validation_rate = 0.0
        self.failures_by_reason.clear()
