"""
HomeAdvisor Plugin
Scrapes lead data from HomeAdvisor pro directory
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

# Import Google Sheets utilities
from .google_sheets_utils import export_to_google_sheets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HomeAdvisorScraper:
    """Scraper for HomeAdvisor professional directories."""

    def __init__(
        self, city: str = "", state: str = "", max_records: Optional[int] = None
    ):
        self.city = city
        self.state = state
        self.max_records = max_records or 50
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )
        self.leads_data: List[Dict[str, str]] = []

    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract email and phone from text using regex patterns."""
        contact_info = {"email": "", "phone": ""}

        # Email patterns
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group()

        # Phone patterns (various formats)
        phone_patterns = [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # 123-456-7890 or 123.456.7890
            r"\(\d{3}\)\s*\d{3}[-.]?\d{4}",  # (123) 456-7890
            r"\b\d{10}\b",  # 1234567890
        ]

        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact_info["phone"] = phone_match.group()
                break

        return contact_info

    def scrape_test_data(self) -> List[Dict[str, str]]:
        """Generate test data for development and testing."""

        test_contractors = []

        # Enhanced test data with HomeAdvisor specifics
        sample_names = [
            "Tom Wilson",
            "Rachel Green",
            "Steve Martin",
            "Diana Prince",
            "Kevin Hart",
            "Laura Palmer",
            "Marcus Johnson",
            "Nina Rodriguez",
            "Paul Anderson",
            "Grace Kelly",
            "Ryan O'Connor",
            "Sophia Turner",
        ]

        sample_businesses = [
            "Elite Home Solutions",
            "ProFix Contractors",
            "HomeAdvisor Pro Services",
            "Quality Home Repair",
            "TrustPro Contractors",
            "Premier Home Care",
            "Reliable Home Solutions",
            "Expert Fix Services",
            "Home Masters Pro",
            "Professional Home Services",
            "Top Rated Contractors",
            "HomeAdvisor Elite",
        ]

        sample_addresses = [
            f"123 Service Lane, {self.city or 'Phoenix'}, {self.state or 'AZ'} 85001",
            f"456 Contractor Ave, {self.city or 'Denver'}, {self.state or 'CO'} 80201",
            f"789 Repair Drive, {self.city or 'Austin'}, {self.state or 'TX'} 73301",
            f"321 Fix Way, {self.city or 'Seattle'}, {self.state or 'WA'} 98101",
            f"654 Professional St, {self.city or 'Portland'}, {self.state or 'OR'} 97201",
            f"987 Expert Blvd, {self.city or 'Atlanta'}, {self.state or 'GA'} 30301",
        ]

        sample_websites = [
            "www.elitehomesolutions.com",
            "www.profixcontractors.com",
            "www.homeadvisorpro.com",
            "www.qualityhomerepair.com",
            "www.trustprocontractors.com",
            "www.premierhomecare.com",
            "www.reliablehomesolutions.com",
            "www.expertfixservices.com",
            "www.homemasterspro.com",
            "www.professionalhomeservices.com",
            "www.topratedcontractors.com",
            "www.homeadvisorelite.com",
        ]

        service_types = [
            "General Contracting",
            "Plumbing",
            "Electrical",
            "HVAC",
            "Roofing",
            "Flooring",
            "Kitchen Remodeling",
            "Bathroom Renovation",
            "Landscaping",
            "Painting",
            "Handyman Services",
            "Home Inspection",
        ]

        # Generate test data
        for i in range(min(self.max_records, len(sample_names))):
            contractor = {
                "Full Name": sample_names[i],
                "Email": f"{sample_names[i].lower().replace(' ', '.')}@{sample_businesses[i].lower().replace(' ', '').replace('homeadvisor', 'ha')}.com",
                "Phone": f"({555 + i:03d}) {100 + i:03d}-{1000 + i:04d}",
                "Business Name": sample_businesses[i],
                "Office Address": sample_addresses[i % len(sample_addresses)],
                "Website": sample_websites[i],
                "Service Type": service_types[i % len(service_types)],
                "Industry": "home_services",
                "Source": "homeadvisor_test",
                "Tag": f"{(self.city or 'unknown').lower().replace(' ', '_')}_homeadvisor",
            }
            test_contractors.append(contractor)

        logger.info(f"Generated {len(test_contractors)} test HomeAdvisor contractors")
        return test_contractors

    def scrape_live_data(self) -> List[Dict[str, str]]:
        """Scrape live data from HomeAdvisor (placeholder implementation)."""

        logger.info("Starting live HomeAdvisor scraping...")

        try:
            # In a real implementation, this would scrape HomeAdvisor Pro directory
            # For now, return test data with a realistic delay
            time.sleep(2)  # Simulate network delay

            # Placeholder: In production, implement actual HomeAdvisor scraping
            # This would involve:
            # 1. Navigate to HomeAdvisor Pro directory
            # 2. Search by location and service type
            # 3. Extract professional profiles
            # 4. Parse contact information

            logger.warning(
                "Live HomeAdvisor scraping not implemented - using test data"
            )
            return self.scrape_test_data()

        except Exception as e:
            logger.error(f"Error in live HomeAdvisor scraping: {e}")
            logger.info("Falling back to test data")
            return self.scrape_test_data()


def run_plugin(config: Dict[str, Any]) -> Dict[str, Any]:
    """Main plugin entry point."""

    city = config.get("city", "")
    state = config.get("state", "")
    max_records = config.get("max_records", 50)
    test_mode = config.get("test_mode", True)
    google_sheet_id = config.get("google_sheet_id")
    google_sheet_name = config.get("google_sheet_name")

    logger.info(
        f"HomeAdvisor Plugin - City: {city}, State: {state}, Test Mode: {test_mode}"
    )

    try:
        scraper = HomeAdvisorScraper(city=city, state=state, max_records=max_records)

        if test_mode:
            logger.info("Running in TEST MODE - generating test data")
            leads = scraper.scrape_test_data()
        else:
            logger.info("Running in LIVE MODE - attempting real scraping")
            leads = scraper.scrape_live_data()

        # Export to Google Sheets if requested
        google_export_success = False
        if google_sheet_id and leads:
            logger.info("Exporting HomeAdvisor leads to Google Sheets...")
            google_export_success = export_to_google_sheets(
                leads,
                google_sheet_id,
                google_sheet_name or f"HomeAdvisor_Leads_{city}",
                "HomeAdvisor",
            )

        return {
            "success": True,
            "leads": leads,
            "count": len(leads),
            "source": "homeadvisor",
            "test_mode": test_mode,
            "google_export_success": google_export_success,
        }

    except Exception as e:
        logger.error(f"HomeAdvisor plugin error: {e}")
        return {
            "success": False,
            "error": str(e),
            "leads": [],
            "count": 0,
            "source": "homeadvisor",
            "test_mode": test_mode,
            "google_export_success": False,
        }


if __name__ == "__main__":
    # Test the plugin
    test_config = {"city": "Miami", "state": "FL", "max_records": 5, "test_mode": True}

    result = run_plugin(test_config)
    print(f"Result: {result['count']} leads found")

    if result["leads"]:
        print("Sample lead:")
        print(result["leads"][0])
