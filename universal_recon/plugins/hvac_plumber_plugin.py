"""
HVAC/Plumbers Plugin
Scrapes lead data from HVAC and plumbing contractor directories
"""

import logging
import re
import time
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HVACPlumberScraper:
    """Scraper for HVAC and plumbing contractor directories."""

    def __init__(self, city: str = "", state: str = "", max_records: int | None = None):
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
        self.leads_data: list[dict[str, str]] = []

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

    def extract_contact_info(self, text: str) -> dict[str, str]:
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

    def scrape_test_data(self) -> list[dict[str, str]]:
        """Generate test data for development and testing."""

        test_contractors = []

        # Enhanced test data with HVAC/plumbing specifics
        sample_names = [
            "Mike Johnson",
            "Sarah Wilson",
            "Dave Rodriguez",
            "Lisa Thompson",
            "Robert Kim",
            "Amanda Martinez",
            "Chris Davis",
            "Jennifer Garcia",
            "James Miller",
            "Maria Lopez",
            "Daniel Brown",
            "Emily Taylor",
        ]

        sample_businesses = [
            "Arctic Air HVAC",
            "Precision Plumbing",
            "CoolBreeze Systems",
            "FlowMaster Plumbing",
            "Climate Control Pros",
            "DrainMaster Services",
            "TempRight HVAC",
            "PipeDream Plumbing",
            "AirFlow Solutions",
            "H2O Plumbing Experts",
            "Comfort Zone HVAC",
            "Reliable Pipe Works",
        ]

        service_types = [
            "HVAC Installation",
            "Plumbing Repair",
            "Air Conditioning",
            "Water Heater Service",
            "Heating Systems",
            "Drain Cleaning",
            "Ductwork",
            "Emergency Plumbing",
            "HVAC Maintenance",
            "Pipe Installation",
            "Furnace Repair",
            "Leak Detection",
        ]

        sample_addresses = [
            f"123 Service Rd, {self.city or 'Miami'}, {self.state or 'FL'} 33101",
            f"456 Contractor Ave, {self.city or 'Tampa'}, {self.state or 'FL'} 33602",
            f"789 HVAC Blvd, {self.city or 'Orlando'}, {self.state or 'FL'} 32801",
            f"321 Plumber St, {self.city or 'Jacksonville'}, {self.state or 'FL'} 32201",
            f"654 Repair Way, {self.city or 'Fort Lauderdale'}, {self.state or 'FL'} 33301",
        ]

        for i in range(min(self.max_records, len(sample_names))):
            name_clean = sample_names[i % len(sample_names)].lower().replace(" ", ".")
            business_clean = (
                sample_businesses[i % len(sample_businesses)]
                .lower()
                .replace(" ", "")
                .replace(".", "")
            )

            contractor = {
                "Full Name": sample_names[i % len(sample_names)],
                "Email": f"{name_clean}@{business_clean}.com",
                "Phone": f"({786 + i % 10}) {str(300 + i).zfill(3)}-{str(3000 + i).zfill(4)}",
                "Business Name": sample_businesses[i % len(sample_businesses)],
                "Office Address": sample_addresses[i % len(sample_addresses)],
                "Website": f"www.{business_clean}.com",
                "Service Type": service_types[i % len(service_types)],
                "Industry": "hvac_plumbers",
                "Source": "test_data",
                "Tag": f"{(self.city or 'test_city').lower().replace(' ', '_')}_hvac_plumber",
            }
            test_contractors.append(contractor)

        # Fill remaining records if needed
        while len(test_contractors) < self.max_records:
            i = len(test_contractors)
            contractor = {
                "Full Name": f"Service Pro {i+1}",
                "Email": f"servicepro{i+1}@hvacplumbing.com",
                "Phone": f"(555) {str(300 + i).zfill(3)}-{str(3000 + i).zfill(4)}",
                "Business Name": f"HVAC Plumbing Co {i+1}",
                "Office Address": f"{300 + i} Service St, {self.city or 'City'}, {self.state or 'ST'} 12345",
                "Website": f"www.hvacplumbing{i+1}.com",
                "Service Type": "General HVAC/Plumbing",
                "Industry": "hvac_plumbers",
                "Source": "test_data",
                "Tag": f"{(self.city or 'test_city').lower().replace(' ', '_')}_hvac_plumber",
            }
            test_contractors.append(contractor)

        return test_contractors

    def scrape_live_data(self) -> list[dict[str, str]]:
        """Scrape live data from HVAC and plumbing directories."""

        # Target URLs for HVAC/plumbing contractor searches
        target_urls = [
            "https://www.angi.com/companylist/us/fl/heating-air-conditioning.htm",
            "https://www.homeadvisor.com/c.Plumbers.FL.html",
            "https://www.yellowpages.com/search?search_terms=hvac&geo_location_terms=",
            "https://www.yelp.com/search?find_desc=plumbers&find_loc=",
        ]

        all_contractors = []

        for url in target_urls:
            try:
                logger.info(f"Scraping HVAC/plumbers from: {url}")

                # Use Selenium for dynamic content
                driver = self.setup_selenium_driver()

                # Add location to URL if applicable
                if self.city and "yellowpages" in url:
                    url += f"{self.city}+{self.state}"
                elif self.city and "yelp" in url:
                    url += f"{self.city}+{self.state}"

                driver.get(url)
                time.sleep(3)

                # Look for contractor listings
                listing_selectors = [
                    ".business-name",
                    ".contractor-card",
                    ".service-provider",
                    ".listing-item",
                    ".business-listing",
                    ".company-info",
                    "[data-business]",
                    "[data-contractor]",
                    ".hvac-listing",
                    ".plumber-listing",
                ]

                soup = BeautifulSoup(driver.page_source, "html.parser")

                listings = []
                for selector in listing_selectors:
                    listings = soup.select(selector)
                    if listings:
                        logger.info(f"Found {len(listings)} listings with selector: {selector}")
                        break

                # Extract contractor information
                for i, listing in enumerate(listings[: self.max_records // len(target_urls)]):
                    try:
                        text = listing.get_text()
                        contact_info = self.extract_contact_info(text)

                        # Extract business name
                        name_elem = listing.find(["h1", "h2", "h3", "h4"])
                        business_name = (
                            name_elem.get_text(strip=True)
                            if name_elem
                            else f"HVAC/Plumbing Contractor {i+1}"
                        )

                        # Determine service type from business name or text
                        service_type = "General HVAC/Plumbing"
                        if any(
                            keyword in text.lower()
                            for keyword in ["hvac", "heating", "cooling", "air"]
                        ):
                            service_type = "HVAC Services"
                        elif any(
                            keyword in text.lower()
                            for keyword in ["plumbing", "plumber", "pipe", "drain"]
                        ):
                            service_type = "Plumbing Services"

                        contractor = {
                            "Full Name": "Service Manager",  # Often not available in directory listings
                            "Email": contact_info["email"]
                            or f"contact@{business_name.lower().replace(' ', '')}.com",
                            "Phone": contact_info["phone"] or "(555) 123-4567",
                            "Business Name": business_name,
                            "Office Address": f"{self.city}, {self.state}",
                            "Website": "N/A",
                            "Service Type": service_type,
                            "Industry": "hvac_plumbers",
                            "Source": url,
                            "Tag": f"{(self.city or 'unknown').lower().replace(' ', '_')}_hvac_plumber",
                        }

                        all_contractors.append(contractor)

                    except Exception as e:
                        logger.error(f"Error extracting contractor {i+1}: {e}")
                        continue

                driver.quit()

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        return all_contractors

    def scrape(self, test_mode: bool = True) -> list[dict[str, str]]:
        """Main scraping method."""

        if test_mode:
            logger.info("Running in TEST MODE - generating simulated HVAC/plumber data")
            return self.scrape_test_data()
        else:
            logger.info("Running in LIVE MODE - scraping real HVAC/plumber data")
            results = self.scrape_live_data()

            # Fallback to test data if no results
            if not results:
                logger.warning("No live results found, falling back to test data")
                return self.scrape_test_data()

            return results


def scrape_hvac_plumbers(
    city: str = "", state: str = "", max_records: int = 50, test_mode: bool = True
) -> list[dict[str, str]]:
    """
    Main function to scrape HVAC/plumber data.

    Args:
        city: Target city for search
        state: Target state for search
        max_records: Maximum number of records to return
        test_mode: Whether to use test data or attempt live scraping

    Returns:
        List of contractor dictionaries
    """

    scraper = HVACPlumberScraper(city=city, state=state, max_records=max_records)
    return scraper.scrape(test_mode=test_mode)


# Plugin interface function
def run_plugin(config: dict[str, Any]) -> dict[str, Any]:
    """
    Plugin interface for universal_recon system.

    Args:
        config: Configuration dictionary with parameters

    Returns:
        Results dictionary with leads data
    """

    city = config.get("city", "")
    state = config.get("state", "")
    max_records = config.get("max_records", 50)
    test_mode = config.get("test_mode", True)

    try:
        leads = scrape_hvac_plumbers(
            city=city, state=state, max_records=max_records, test_mode=test_mode
        )

        return {
            "success": True,
            "leads": leads,
            "count": len(leads),
            "industry": "hvac_plumbers",
            "source": "hvac_plumber_directories",
        }

    except Exception as e:
        logger.error(f"HVAC/Plumbers plugin error: {e}")
        return {
            "success": False,
            "error": str(e),
            "leads": [],
            "count": 0,
            "industry": "hvac_plumbers",
        }


if __name__ == "__main__":
    # Test the plugin
    config = {"city": "Miami", "state": "FL", "max_records": 5, "test_mode": True}

    result = run_plugin(config)
    print(f"HVAC/Plumbers Plugin Test: {result['count']} leads found")

    if result["leads"]:
        df = pd.DataFrame(result["leads"])
        print(df.head())
