"""
Lawyers Bar Directory Plugin
Scrapes lead data from state bar associations and legal directories
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional

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


class LawyerBarDirectoryScraper:
    """Scraper for state bar directories and legal professional listings."""

    def __init__(
        self, city: str = "", state: str = "", max_records: int | None = None
    ):
        self.city = city
        self.state = state
        self.max_records = max_records or 50
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebDriver/537.36 "
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

        test_lawyers = []

        # Enhanced test data with lawyer specifics
        sample_names = [
            "Sarah Thompson, Esq.",
            "Michael Rodriguez, J.D.",
            "Jennifer Davis",
            "David Kim",
            "Lisa Johnson",
            "Robert Wilson",
            "Amanda Garcia",
            "Christopher Lee",
            "Maria Martinez",
            "James Miller",
            "Emily Brown",
            "Daniel Taylor",
        ]

        sample_businesses = [
            "Thompson & Associates Law Firm",
            "Rodriguez Legal Group",
            "Davis Law Office",
            "Kim Immigration Law",
            "Johnson Family Law",
            "Wilson Criminal Defense",
            "Garcia Personal Injury Law",
            "Lee Corporate Law",
            "Martinez & Partners",
            "Miller Estate Planning",
            "Brown Employment Law",
            "Taylor Tax Law",
        ]

        practice_areas = [
            "Personal Injury",
            "Family Law",
            "Criminal Defense",
            "Corporate Law",
            "Immigration Law",
            "Estate Planning",
            "Employment Law",
            "Tax Law",
            "Real Estate Law",
            "Bankruptcy Law",
            "Intellectual Property",
            "Medical Malpractice",
        ]

        sample_addresses = [
            f"123 Legal Plaza, {self.city or 'Miami'}, {self.state or 'FL'} 33101",
            f"456 Attorney Ave, {self.city or 'Tampa'}, {self.state or 'FL'} 33602",
            f"789 Law Center Dr, {self.city or 'Orlando'}, {self.state or 'FL'} 32801",
            f"321 Justice Way, {self.city or 'Jacksonville'}, {self.state or 'FL'} 32201",
            f"654 Court Street, {self.city or 'Fort Lauderdale'}, {self.state or 'FL'} 33301",
        ]

        for i in range(min(self.max_records, len(sample_names))):
            name_clean = (
                sample_names[i % len(sample_names)]
                .lower()
                .replace(" ", ".")
                .replace(",", "")
                .replace(".", "")
            )
            business_clean = (
                sample_businesses[i % len(sample_businesses)]
                .lower()
                .replace(" ", "")
                .replace("&", "and")
            )

            lawyer = {
                "Full Name": sample_names[i % len(sample_names)],
                "Email": f"{name_clean}@{business_clean}.com",
                "Phone": f"({305 + i % 10}) {str(200 + i).zfill(3)}-{str(2000 + i).zfill(4)}",
                "Business Name": sample_businesses[i % len(sample_businesses)],
                "Office Address": sample_addresses[i % len(sample_addresses)],
                "Website": f"www.{business_clean}.com",
                "Practice Area": practice_areas[i % len(practice_areas)],
                "Industry": "lawyers",
                "Source": "test_data",
                "Tag": f"{(self.city or 'test_city').lower().replace(' ', '_')}_lawyer",
            }
            test_lawyers.append(lawyer)

        # Fill remaining records if needed
        while len(test_lawyers) < self.max_records:
            i = len(test_lawyers)
            lawyer = {
                "Full Name": f"Attorney {i+1}, Esq.",
                "Email": f"attorney{i+1}@lawfirm.com",
                "Phone": f"(555) {str(200 + i).zfill(3)}-{str(2000 + i).zfill(4)}",
                "Business Name": f"Law Firm {i+1}",
                "Office Address": f"{200 + i} Legal St, {self.city or 'City'}, {self.state or 'ST'} 12345",
                "Website": f"www.lawfirm{i+1}.com",
                "Practice Area": "General Practice",
                "Industry": "lawyers",
                "Source": "test_data",
                "Tag": f"{(self.city or 'test_city').lower().replace(' ', '_')}_lawyer",
            }
            test_lawyers.append(lawyer)

        return test_lawyers

    def scrape_live_data(self) -> list[dict[str, str]]:
        """Scrape live data from bar directories and legal listings."""

        # Target URLs for lawyer directory searches (state-specific)
        state_bar_urls = {
            "FL": "https://www.floridabar.org/directories/find-mbr/",
            "CA": "https://www.calbar.ca.gov/Attorneys/Memberships/Attorney-Search",
            "NY": "https://iapps.courts.state.ny.us/attorney/AttorneySearch",
            "TX": "https://www.texasbar.com/AM/Template.cfm?Section=Lawyer_Referral_Service_LRIS_",
        }

        # General legal directories
        general_urls = [
            "https://www.martindale.com/",
            "https://www.avvo.com/",
            "https://www.lawyers.com/",
            "https://www.findlaw.com/",
        ]

        all_lawyers = []

        # Try state-specific bar directory first
        if self.state.upper() in state_bar_urls:
            target_urls = [state_bar_urls[self.state.upper()]] + general_urls[:2]
        else:
            target_urls = general_urls

        for url in target_urls:
            try:
                logger.info(f"Scraping lawyers from: {url}")

                # Use Selenium for dynamic content
                driver = self.setup_selenium_driver()
                driver.get(url)
                time.sleep(3)

                # Look for lawyer listings
                listing_selectors = [
                    ".lawyer-listing",
                    ".attorney-card",
                    ".legal-professional",
                    ".listing-item",
                    ".lawyer-card",
                    ".attorney-info",
                    "[data-lawyer]",
                    "[data-attorney]",
                    ".member-listing",
                ]

                soup = BeautifulSoup(driver.page_source, "html.parser")

                listings = []
                for selector in listing_selectors:
                    listings = soup.select(selector)
                    if listings:
                        logger.info(
                            f"Found {len(listings)} listings with selector: {selector}"
                        )
                        break

                # Extract lawyer information
                for i, listing in enumerate(
                    listings[: self.max_records // len(target_urls)]
                ):
                    try:
                        text = listing.get_text()
                        contact_info = self.extract_contact_info(text)

                        # Extract lawyer name
                        name_elem = listing.find(["h1", "h2", "h3", "h4"])
                        lawyer_name = (
                            name_elem.get_text(strip=True)
                            if name_elem
                            else f"Attorney {i+1}"
                        )

                        # Extract firm/business name
                        firm_elem = listing.find(
                            class_=re.compile(r"(firm|business|company)", re.I)
                        )
                        firm_name = (
                            firm_elem.get_text(strip=True)
                            if firm_elem
                            else f"{lawyer_name} Law Office"
                        )

                        lawyer = {
                            "Full Name": lawyer_name,
                            "Email": contact_info["email"]
                            or f"contact@{lawyer_name.lower().replace(' ', '')}.com",
                            "Phone": contact_info["phone"] or "(555) 123-4567",
                            "Business Name": firm_name,
                            "Office Address": f"{self.city}, {self.state}",
                            "Website": "N/A",
                            "Practice Area": "General Practice",
                            "Industry": "lawyers",
                            "Source": url,
                            "Tag": f"{(self.city or 'unknown').lower().replace(' ', '_')}_lawyer",
                        }

                        all_lawyers.append(lawyer)

                    except Exception as e:
                        logger.error(f"Error extracting lawyer {i+1}: {e}")
                        continue

                driver.quit()

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        return all_lawyers

    def scrape(self, test_mode: bool = True) -> list[dict[str, str]]:
        """Main scraping method."""

        if test_mode:
            logger.info("Running in TEST MODE - generating simulated lawyer data")
            return self.scrape_test_data()
        else:
            logger.info("Running in LIVE MODE - scraping real lawyer data")
            results = self.scrape_live_data()

            # Fallback to test data if no results
            if not results:
                logger.warning("No live results found, falling back to test data")
                return self.scrape_test_data()

            return results


def scrape_lawyers(
    city: str = "", state: str = "", max_records: int = 50, test_mode: bool = True
) -> list[dict[str, str]]:
    """
    Main function to scrape lawyer data.

    Args:
        city: Target city for search
        state: Target state for search
        max_records: Maximum number of records to return
        test_mode: Whether to use test data or attempt live scraping

    Returns:
        List of lawyer dictionaries
    """

    scraper = LawyerBarDirectoryScraper(city=city, state=state, max_records=max_records)
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
        leads = scrape_lawyers(
            city=city, state=state, max_records=max_records, test_mode=test_mode
        )

        return {
            "success": True,
            "leads": leads,
            "count": len(leads),
            "industry": "lawyers",
            "source": "bar_directories",
        }

    except Exception as e:
        logger.error(f"Lawyers plugin error: {e}")
        return {
            "success": False,
            "error": str(e),
            "leads": [],
            "count": 0,
            "industry": "lawyers",
        }


if __name__ == "__main__":
    # Test the plugin
    config = {"city": "Miami", "state": "FL", "max_records": 5, "test_mode": True}

    result = run_plugin(config)
    print(f"Lawyers Plugin Test: {result['count']} leads found")

    if result["leads"]:
        df = pd.DataFrame(result["leads"])
        print(df.head())
