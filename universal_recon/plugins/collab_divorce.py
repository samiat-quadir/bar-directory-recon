"""Collaborative Divorce Plugin for universal_recon.

This plugin specializes in extracting data from collaborative divorce 
professional directories and mediation services.
"""

import logging
from typing import Any, Dict, Iterator

logger = logging.getLogger(__name__)


class CollabDivorcePlugin:
    """Plugin for extracting collaborative divorce professional data."""

    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        return "collab_divorce"

    def fetch(self) -> Iterator[Dict[str, Any]]:
        """Fetch raw collaborative divorce professional data.

        Yields:
            Dict[str, Any]: Raw professional data records
        """
        # Sample collaborative divorce professionals for testing
        sample_professionals = [
            {
                "name": "Dr. Sarah Johnson",
                "type": "collaborative_attorney",
                "specialization": "Family Law",
                "location": "Seattle, WA",
                "phone": "(206) 555-0123",
                "email": "sjohnson@collablaw.com",
                "certifications": ["Collaborative Professional", "Family Mediator"],
                "practice_areas": ["Divorce", "Child Custody", "Property Division"]
            },
            {
                "name": "Michael Chen",
                "type": "divorce_coach",
                "specialization": "Life Coaching",
                "location": "Portland, OR", 
                "phone": "(503) 555-0456",
                "email": "mchen@divorcecoach.com",
                "certifications": ["Certified Divorce Coach", "Mental Health Counselor"],
                "practice_areas": ["Emotional Support", "Co-parenting", "Communication"]
            },
            {
                "name": "Jennifer Martinez",
                "type": "financial_specialist",
                "specialization": "Financial Planning",
                "location": "San Francisco, CA",
                "phone": "(415) 555-0789",
                "email": "jmartinez@financialdivorce.com",
                "certifications": ["CDFA", "CPA"],
                "practice_areas": ["Asset Division", "Retirement Planning", "Tax Planning"]
            }
        ]

        for professional in sample_professionals:
            yield professional

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw professional data into standardized format.

        Args:
            raw_data: Raw professional data record from fetch()

        Returns:
            Dict[str, Any]: Transformed data in standard format
        """
        transformed = {
            "professional_name": raw_data.get("name", "").strip(),
            "professional_type": raw_data.get("type", "unknown"),
            "specialization": raw_data.get("specialization", ""),
            "location": raw_data.get("location", ""),
            "contact_phone": self._format_phone(raw_data.get("phone", "")),
            "contact_email": raw_data.get("email", "").lower().strip(),
            "certifications": raw_data.get("certifications", []),
            "practice_areas": raw_data.get("practice_areas", []),
            "data_source": "collab_divorce",
            "record_type": "collaborative_professional"
        }
        return transformed

    def validate(self, transformed_data: Dict[str, Any]) -> bool:
        """Validate transformed professional data meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if data passes validation, False otherwise
        """
        required_fields = ["professional_name", "professional_type"]
        
        # Check required fields are present and non-empty
        for field in required_fields:
            if not transformed_data.get(field):
                return False

        # Validate professional type is one of expected values
        valid_types = [
            "collaborative_attorney", 
            "divorce_coach", 
            "financial_specialist",
            "child_specialist",
            "mediator"
        ]
        if transformed_data.get("professional_type") not in valid_types:
            return False

        # Validate email format if provided
        email = transformed_data.get("contact_email")
        if email and "@" not in email:
            return False

        return True

    def _format_phone(self, phone: str) -> str:
        """Format phone number to consistent format."""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Format as (XXX) XXX-XXXX if we have 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # Handle 1-XXX-XXX-XXXX format
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            # Return original if we can't format
            return phone


def extract_collab_divorce_data(driver: Any, context: Any) -> Dict[str, Any]:
    """Legacy function for backward compatibility.

    Args:
        driver: WebDriver instance (unused in sample implementation)
        context: Extraction context dictionary

    Returns:
        Dictionary containing extracted collaborative divorce data
    """
    # This maintains backward compatibility with existing code
    plugin = CollabDivorcePlugin()
    # Return the first validated transformed record for compatibility
    for raw_record in plugin.fetch():
        transformed = plugin.transform(raw_record)
        if plugin.validate(transformed):
            return transformed
    return {}