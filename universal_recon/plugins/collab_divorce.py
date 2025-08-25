"""Collaborative divorce attorney directory plugin.

This plugin specializes in extracting and processing data from 
collaborative divorce attorney directories and legal mediation services.
Focuses on collaborative law practitioners and family mediation specialists.
"""

import re
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin, urlparse

from .base import Plugin


class CollabDivorcePlugin(Plugin):
    """Plugin for collaborative divorce attorney directories."""

    def __init__(self, base_url: str = None):
        """Initialize the collaborative divorce plugin.
        
        Args:
            base_url: Base URL for the collaborative divorce directory
        """
        self.base_url = base_url or "https://collaborativedivorce.org"
        self._name = "collab_divorce"
        
    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        return self._name

    def fetch(self) -> Iterator[Dict[str, Any]]:
        """Fetch raw data from collaborative divorce directories.

        This is a mock implementation for offline testing.
        In production, this would scrape actual collaborative divorce directories.

        Yields:
            Dict[str, Any]: Raw attorney data records
        """
        # Mock data for offline testing
        mock_attorneys = [
            {
                "name": "Dr. Sarah Johnson, JD",
                "practice_areas": ["Collaborative Divorce", "Family Mediation"],
                "location": "San Francisco, CA",
                "phone": "(415) 555-0123",
                "email": "sarah.johnson@collablaw.com",
                "certifications": ["Collaborative Process Certified"],
                "years_experience": 15,
                "collaborative_cases": 150,
                "raw_url": "https://collaborativedivorce.org/attorneys/sarah-johnson"
            },
            {
                "name": "Michael Chen, Esq.",
                "practice_areas": ["Collaborative Law", "Child Custody Mediation"],
                "location": "Portland, OR", 
                "phone": "(503) 555-0456",
                "email": "m.chen@pacificmediation.com",
                "certifications": ["International Academy of Collaborative Professionals"],
                "years_experience": 12,
                "collaborative_cases": 89,
                "raw_url": "https://collaborativedivorce.org/attorneys/michael-chen"
            }
        ]
        
        for attorney in mock_attorneys:
            yield attorney

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw attorney data into standardized format.

        Args:
            raw_data: Raw data record from fetch()

        Returns:
            Dict[str, Any]: Transformed data in standard format
        """
        # Extract and normalize name with safe handling
        name_raw = raw_data.get("name", "")
        name = str(name_raw).strip() if name_raw is not None else ""
        
        # Extract location components with safe handling
        location_raw = raw_data.get("location", "")
        location = str(location_raw) if isinstance(location_raw, (str, int, float)) else ""
        city, state = self._parse_location(location)
        
        # Normalize phone number with safe handling
        phone_raw = raw_data.get("phone", "")
        phone = self._normalize_phone(str(phone_raw) if phone_raw is not None else "")
        
        # Extract email domain for firm identification with safe handling
        email_raw = raw_data.get("email", "")
        email = str(email_raw).lower().strip() if email_raw is not None else ""
        firm_domain = self._extract_domain(email)
        
        # Calculate experience score with safe handling
        years_exp = raw_data.get("years_experience", 0)
        collab_cases = raw_data.get("collaborative_cases", 0)
        
        # Convert to integers safely
        try:
            years_exp = int(years_exp) if years_exp is not None else 0
        except (ValueError, TypeError):
            years_exp = 0
            
        try:
            collab_cases = int(collab_cases) if collab_cases is not None else 0
        except (ValueError, TypeError):
            collab_cases = 0
            
        experience_score = self._calculate_experience_score(years_exp, collab_cases)
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "city": city,
            "state": state,
            "practice_areas": raw_data.get("practice_areas", []),
            "certifications": raw_data.get("certifications", []),
            "years_experience": years_exp,
            "collaborative_cases": collab_cases,
            "experience_score": experience_score,
            "firm_domain": firm_domain,
            "source_url": raw_data.get("raw_url", ""),
            "plugin_name": self.name,
            "record_type": "collaborative_attorney"
        }

    def validate(self, transformed_data: Dict[str, Any]) -> bool:
        """Validate that transformed data meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if data passes validation, False otherwise
        """
        required_fields = ["name", "email", "phone", "city", "state"]
        
        # Check required fields are present and non-empty
        for field in required_fields:
            if not transformed_data.get(field):
                return False
        
        # Validate email format
        email = transformed_data.get("email", "")
        if not self._is_valid_email(email):
            return False
            
        # Validate phone format
        phone = transformed_data.get("phone", "")
        if not self._is_valid_phone(phone):
            return False
            
        # Validate state code
        state = transformed_data.get("state", "")
        if len(state) != 2 or not state.isalpha():
            return False
            
        return True

    def _parse_location(self, location: str) -> tuple[str, str]:
        """Parse city and state from location string."""
        if not location:
            return "", ""
            
        parts = location.split(",")
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip()
            # Extract state code if full state name
            state_match = re.search(r'\b([A-Z]{2})\b', state)
            if state_match:
                state = state_match.group(1)
            return city, state
        
        return location.strip(), ""

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format."""
        if not phone:
            return ""
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX for 10-digit numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't normalize

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or "@" not in email:
            return ""
        
        return email.split("@")[1].lower()

    def _calculate_experience_score(self, years: int, cases: int) -> float:
        """Calculate experience score based on years and case count."""
        # Weight years of experience and collaborative cases handled
        year_score = min(years * 2, 30)  # Max 30 points for years
        case_score = min(cases * 0.5, 70)  # Max 70 points for cases
        
        return round(year_score + case_score, 1)

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        
        # Accept various formats
        patterns = [
            r'^\(\d{3}\) \d{3}-\d{4}$',  # (123) 456-7890
            r'^\d{3}-\d{3}-\d{4}$',      # 123-456-7890
            r'^\d{10}$',                 # 1234567890
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)


# Plugin registry entry
def get_plugin() -> CollabDivorcePlugin:
    """Factory function to create plugin instance."""
    return CollabDivorcePlugin()