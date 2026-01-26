"""
Deduplication Report Generator

Provides transparency into URL and record deduplication,
logging what was removed and why.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
import json


class DeduplicationReport:
    """Tracks and reports on duplicate removal during extraction."""
    
    def __init__(self):
        """Initialize deduplication report tracker."""
        self.url_duplicates: List[str] = []
        self.record_duplicates: List[Dict[str, Any]] = []
        self.url_total = 0
        self.url_unique = 0
        self.record_total = 0
        self.record_unique = 0
    
    def track_url_deduplication(
        self, 
        original_urls: List[str], 
        unique_urls: List[str]
    ) -> None:
        """
        Track URLs removed during deduplication.
        
        Args:
            original_urls: Full list including duplicates
            unique_urls: List after deduplication
        """
        self.url_total = len(original_urls)
        self.url_unique = len(unique_urls)
        
        # Track which URLs were duplicates (simple approach: count occurrences)
        seen = set()
        for url in original_urls:
            if url in seen:
                self.url_duplicates.append(url)
            else:
                seen.add(url)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for deduplication.
        
        Returns:
            Dictionary with deduplication counts and percentages
        """
        url_removed = self.url_total - self.url_unique
        url_removal_pct = (url_removed / self.url_total * 100) if self.url_total > 0 else 0
        
        return {
            'urls': {
                'total': self.url_total,
                'unique': self.url_unique,
                'duplicates_removed': url_removed,
                'removal_percentage': round(url_removal_pct, 2)
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def save_report(self, output_dir: Path, base_name: str) -> Path:
        """
        Save deduplication report to JSON file.
        
        Args:
            output_dir: Directory to save report
            base_name: Base filename for report
            
        Returns:
            Path to saved report file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_data = self.get_summary()
        
        # Add sample duplicates if any
        if self.url_duplicates:
            # Include up to 10 examples
            report_data['url_duplicate_examples'] = self.url_duplicates[:10]
        
        report_path = output_dir / f"{base_name}_deduplication_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        return report_path
    
    def log_summary(self, logger) -> None:
        """
        Log deduplication summary to provided logger.
        
        Args:
            logger: Logger instance to use
        """
        summary = self.get_summary()
        
        if summary['urls']['duplicates_removed'] > 0:
            logger.info(
                f"Deduplication: {summary['urls']['total']} URLs → "
                f"{summary['urls']['unique']} unique "
                f"({summary['urls']['duplicates_removed']} duplicates removed, "
                f"{summary['urls']['removal_percentage']}%)"
            )
        else:
            logger.info(
                f"Deduplication: {summary['urls']['total']} URLs, no duplicates found"
            )


def deduplicate_with_tracking(
    items: List[str],
    report: DeduplicationReport
) -> List[str]:
    """
    Deduplicate list while tracking what was removed.
    
    Args:
        items: Original list (may contain duplicates)
        report: DeduplicationReport instance to track removals
        
    Returns:
        Deduplicated list (order preserved)
    """
    # Use dict.fromkeys() to preserve order while removing duplicates
    # This is the same algorithm used in orchestrator.py line 190
    unique_items = list(dict.fromkeys(items))
    
    # Track the deduplication
    report.track_url_deduplication(items, unique_items)
    
    return unique_items
