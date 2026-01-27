"""
Validation summary and scoring - stub for PR compatibility.
Full implementation in feature/integrity-validation-threshold.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationSummary:
    """Stub placeholder for ValidationSummary - full implementation in THRESH PR."""
    
    total_records: int = 0
    passed_validation: int = 0
    failed_validation: int = 0
    validation_rate: float = 0.0
    failures_by_reason: Dict[str, int] = field(default_factory=dict)
    
    def add_validation_result(self, passed: bool, reason: Optional[str] = None) -> None:
        """Stub method."""
        pass
    
    def get_summary_dict(self) -> Dict[str, Any]:
        """Stub method."""
        return {}
