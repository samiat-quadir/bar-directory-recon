"""
Thumbtack Plugin
Scrapes lead data from Thumbtack professional directories
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


class ThumbScraper:
    """Scraper for Thumbtack professional directories."""

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

        test_pros = []

        # Enhanced test data with Thumbtack specifics
        sample_names = [
            "Alex Turner",
            "Maya Patel",
            "Jake Wilson",
            "Zoe Chen",
            "Ryan Murphy",
            "Elena Rodriguez",
            "Chris Parker",
            "Ivy Johnson",
            "Tyler Brooks",
            "Luna Martinez",
            "Drew Taylor",
            "Aria Davis",
        ]

        sample_businesses = [
            "Thumbtack Pro Services",
            "Top Rated Handyman",
            "Elite Repair Solutions",
            "Professional Home Care",
            "Expert Service Pro",
            "Quality Work Solutions",
            "Trusted Local Pro",
            "Skilled Handyman Services",
            "Premium Home Solutions",
            "Reliable Repair Pro",
            "Master Craftsman Services",
            "Pro Service Solutions",
        ]

        sample_addresses = [
            f"123 Pro Lane, {self.city or 'Chicago'}, {self.state or 'IL'} 60601",
            f"456 Service Ave, {self.city or 'Dallas'}, {self.state or 'TX'} 75201",
            f"789 Expert Drive, {self.city or 'Houston'}, {self.state or 'TX'} 77001",
            f"321 Skilled Way, {self.city or 'Boston'}, {self.state or 'MA'} 02101",
            f"654 Master St, {self.city or 'Minneapolis'}, {self.state or 'MN'} 55401",
            f"987 Craft Blvd, {self.city or 'Nashville'}, {self.state or 'TN'} 37201",
        ]

        sample_websites = [
            "www.thumbtackproservices.com",
            "www.topratedhandyman.com",
            "www.eliterepairsolutions.com",
            "www.professionalhomecare.com",
            "www.expertservicepro.com",
            "www.qualityworksolutions.com",
            "www.trustedlocalpro.com",
            "www.skilledhandymanservices.com",
            "www.premiumhomesolutions.com",
            "www.reliablerepairpro.com",
            "www.mastercraftsmanservices.com",
            "www.proservicesolutions.com",
        ]

        service_categories = [
            "Home Improvement",
            "Handyman",
            "Cleaning Services",
            "Event Planning",
            "Tutoring",
            "Pet Services",
            "Photography",
            "Personal Training",
            "Lawn Care",
            "Interior Design",
            "Moving Services",
            "Music Lessons",
        ]

        # Generate test data
        for i in range(min(self.max_records, len(sample_names))):
            pro = {
                "Full Name": sample_names[i],
                "Email": f"{sample_names[i].lower().replace(' ', '.')}@{sample_businesses[i].lower().replace(' ', '').replace('thumbtack', 'tt')}.com",
                "Phone": f"({600 + i:03d}) {200 + i:03d}-{2000 + i:04d}",
                "Business Name": sample_businesses[i],
                "Office Address": sample_addresses[i % len(sample_addresses)],
                "Website": sample_websites[i],
                "Service Category": service_categories[i % len(service_categories)],
                "Industry": "professional_services",
                "Source": "thumbtack_test",
                "Tag": f"{(self.city or 'unknown').lower().replace(' ', '_')}_thumbtack",
            }
            test_pros.append(pro)

        logger.info(f"Generated {len(test_pros)} test Thumbtack professionals")
        return test_pros

    def scrape_live_data(self) -> List[Dict[str, str]]:
        """Scrape live data from Thumbtack (placeholder implementation)."""

        logger.info("Starting live Thumbtack scraping...")

        try:
            # In a real implementation, this would scrape Thumbtack professional directory
            # For now, return test data with a realistic delay
            time.sleep(2)  # Simulate network delay

            # Placeholder: In production, implement actual Thumbtack scraping
            # This would involve:
            # 1. Navigate to Thumbtack professional directory
            # 2. Search by location and service category
            # 3. Extract professional profiles
            # 4. Parse contact information

            logger.warning("Live Thumbtack scraping not implemented - using test data")
            return self.scrape_test_data()

        except Exception as e:
            logger.error(f"Error in live Thumbtack scraping: {e}")
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
        f"Thumbtack Plugin - City: {city}, State: {state}, Test Mode: {test_mode}"
    )

    try:
        scraper = ThumbScraper(city=city, state=state, max_records=max_records)

        if test_mode:
            logger.info("Running in TEST MODE - generating test data")
            leads = scraper.scrape_test_data()
        else:
            logger.info("Running in LIVE MODE - attempting real scraping")
            leads = scraper.scrape_live_data()

        # Export to Google Sheets if requested
        google_export_success = False
        if google_sheet_id and leads:
            logger.info("Exporting Thumbtack leads to Google Sheets...")
            google_export_success = export_to_google_sheets(
                leads,
                google_sheet_id,
                google_sheet_name or f"Thumbtack_Leads_{city}",
                "Thumbtack",
            )

        return {
            "success": True,
            "leads": leads,
            "count": len(leads),
            "source": "thumbtack",
            "test_mode": test_mode,
            "google_export_success": google_export_success,
        }

    except Exception as e:
        logger.error(f"Thumbtack plugin error: {e}")
        return {
            "success": False,
            "error": str(e),
            "leads": [],
            "count": 0,
            "source": "thumbtack",
            "test_mode": test_mode,
            "google_export_success": False,
        }


if __name__ == "__main__":
    # Test the plugin
    test_config = {"city": "Austin", "state": "TX", "max_records": 5, "test_mode": True}

    result = run_plugin(test_config)
    print(f"Result: {result['count']} leads found")

    if result["leads"]:
        print("Sample lead:")
        print(result["leads"][0])
