"""
Realtor Directory Plugin
Scrapes lead data from directories.apps.realtor.com
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtorDirectoryScraper:
    """Scraper for realtor directory data."""

    def __init__(self, base_url: str = "https://directories.apps.realtor/", max_records: Optional[int] = None):
        self.base_url = base_url
        self.max_records = max_records
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        })
        self.leads_data: List[Dict[str, str]] = []

    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def extract_member_details(self, member_element: Any) -> Optional[Dict[str, str]]:
        """Extract details from a member listing element."""
        try:
            # Extract name
            name_elem = member_element.find('h3', class_='member-name') or member_element.find('.name')
            name = name_elem.get_text(strip=True) if name_elem else ""

            # Extract business name
            business_elem = member_element.find('.business-name') or member_element.find('.company')
            business_name = business_elem.get_text(strip=True) if business_elem else ""

            # Extract email (may be obfuscated)
            email_elem = member_element.find('a', href=lambda x: x and 'mailto:' in x)
            email = ""
            if email_elem:
                email = email_elem.get('href', '').replace('mailto:', '')
            else:
                # Look for obfuscated email patterns
                email_text = member_element.find(text=lambda x: x and '@' in x)
                if email_text:
                    # Basic deobfuscation for common patterns
                    email = email_text.strip().replace(' [at] ', '@').replace(' [dot] ', '.')

            # Extract phone number
            phone_elem = member_element.find('a', href=lambda x: x and 'tel:' in x)
            phone = ""
            if phone_elem:
                phone = phone_elem.get_text(strip=True)
            else:
                # Look for phone patterns in text
                import re
                phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
                phone_match = re.search(phone_pattern, member_element.get_text())
                if phone_match:
                    phone = phone_match.group(1)

            # Extract address
            address_elem = member_element.find('.address') or member_element.find('.location')
            address = address_elem.get_text(strip=True) if address_elem else ""

            # Only return if we have at least a name
            if name:
                return {
                    'name': name,
                    'business_name': business_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'scraped_at': datetime.now().isoformat()
                }

        except Exception as e:
            logger.warning(f"Error extracting member details: {e}")

        return None

    def scrape_with_requests(self, url: str) -> List[Dict[str, str]]:
        """Scrape using requests and BeautifulSoup (for static content)."""
        leads: List[Dict[str, str]] = []

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Common selectors for member listings
            member_selectors = [
                '.member-listing',
                '.member-card',
                '.realtor-card',
                '.agent-listing',
                '.member-item',
                '.directory-entry'
            ]

            members = []
            for selector in member_selectors:
                members = soup.select(selector)
                if members:
                    break

            if not members:
                # Fallback: look for any card-like structures
                all_divs = soup.find_all(['div', 'article'])
                members = [div for div in all_divs if div.get('class') and any(
                    keyword in ' '.join(div.get('class', [])).lower()
                    for keyword in ['member', 'card', 'listing', 'agent', 'realtor']
                )] if all_divs else []

            logger.info(f"Found {len(members)} potential member elements")

            for member in members:
                if self.max_records and len(leads) >= self.max_records:
                    break

                lead_data = self.extract_member_details(member)
                if lead_data:
                    leads.append(lead_data)

        except Exception as e:
            logger.error(f"Error scraping with requests: {e}")

        return leads

    def scrape_with_selenium(self, url: str) -> List[Dict[str, str]]:
        """Scrape using Selenium (for dynamic content)."""
        leads: List[Dict[str, str]] = []
        driver = None

        try:
            driver = self.setup_selenium_driver()
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Try to load more content if pagination exists
            try:
                load_more_selectors = [
                    'button[contains(text(), "Load More")]',
                    'button[contains(text(), "Show More")]',
                    '.load-more',
                    '.show-more',
                    '[data-action="load-more"]'
                ]

                for selector in load_more_selectors:
                    try:
                        load_more_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        if load_more_btn.is_displayed():
                            driver.execute_script("arguments[0].click();", load_more_btn)
                            time.sleep(2)
                            break
                    except Exception:
                        continue

            except Exception:
                logger.info("No load more button found or clickable")

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Use same extraction logic as requests method
            member_selectors = [
                '.member-listing',
                '.member-card',
                '.realtor-card',
                '.agent-listing',
                '.member-item',
                '.directory-entry'
            ]

            members = []
            for selector in member_selectors:
                members = soup.select(selector)
                if members:
                    break

            logger.info(f"Found {len(members)} member elements with Selenium")

            for member in members:
                if self.max_records and len(leads) >= self.max_records:
                    break

                lead_data = self.extract_member_details(member)
                if lead_data:
                    leads.append(lead_data)

        except Exception as e:
            logger.error(f"Error scraping with Selenium: {e}")

        finally:
            if driver:
                driver.quit()

        return leads

    def scrape_directory(self, search_params: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Main scraping method."""

        # Construct URL with search parameters
        url = self.base_url
        if not url.endswith('?type=member'):
            url = urljoin(url, '?type=member')

        if search_params:
            for key, value in search_params.items():
                url += f"&{key}={value}"

        logger.info(f"Scraping URL: {url}")

        # Try requests first (faster)
        leads = self.scrape_with_requests(url)

        # If no results, try Selenium (handles dynamic content)
        if not leads:
            logger.info("No results with requests, trying Selenium...")
            leads = self.scrape_with_selenium(url)

        logger.info(f"Successfully scraped {len(leads)} leads")
        self.leads_data = leads

        return leads

    def save_to_csv(self, output_path: str) -> str:
        """Save leads data to CSV file."""

        if not self.leads_data:
            logger.warning("No data to save")
            return output_path

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Define CSV columns
        columns = ['name', 'email', 'phone', 'business_name', 'address', 'scraped_at']

        # Create DataFrame and save
        df = pd.DataFrame(self.leads_data)

        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = ''

        # Reorder columns
        df = df[columns]

        # Save to CSV
        df.to_csv(output_path, index=False, encoding='utf-8')

        logger.info(f"Saved {len(df)} leads to {output_path}")
        return output_path

    def save_to_google_sheets(self, sheet_id: Optional[str] = None, credentials_path: Optional[str] = None) -> bool:
        """Save leads data to Google Sheets (optional)."""

        if not self.leads_data:
            logger.warning("No data to save to Google Sheets")
            return False

        try:
            import gspread
            from google.auth import default

            # Authentication
            if credentials_path and os.path.exists(credentials_path):
                gc = gspread.service_account(filename=credentials_path)
            else:
                # Try default credentials
                creds, _ = default()
                gc = gspread.authorize(creds)

            # Open spreadsheet
            if sheet_id:
                sheet = gc.open_by_key(sheet_id)
            else:
                sheet = gc.create('Realtor Directory Leads')
                logger.info(f"Created new Google Sheet: {sheet.url}")

            # Get first worksheet
            worksheet = sheet.get_worksheet(0)

            # Clear existing data
            worksheet.clear()

            # Prepare data
            columns = ['name', 'email', 'phone', 'business_name', 'address', 'scraped_at']
            df = pd.DataFrame(self.leads_data)

            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = ''

            # Convert to list format for gspread
            data = [columns] + df[columns].values.tolist()

            # Update worksheet
            worksheet.update(range_name='A1', values=data)

            logger.info(f"Successfully uploaded {len(df)} leads to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Error uploading to Google Sheets: {e}")
            return False


def scrape_realtor_directory(
    output_path: Optional[str] = None,
    max_records: Optional[int] = None,
    search_params: Optional[Dict[str, str]] = None,
    google_sheet_id: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Main function to scrape realtor directory.

    Args:
        output_path: Path to save CSV file
        max_records: Maximum number of records to scrape
        search_params: Dictionary of search parameters
        google_sheet_id: Google Sheets ID for upload
        verbose: Enable verbose logging

    Returns:
        Dictionary with results and metadata
    """

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Default output path
    if not output_path:
        output_path = os.path.join("outputs", "realtor_leads.csv")

    # Create scraper instance
    scraper = RealtorDirectoryScraper(max_records=max_records)

    # Log start time
    start_time = datetime.now()
    logger.info(f"Starting realtor directory scrape at {start_time}")

    try:
        # Scrape data
        leads = scraper.scrape_directory(search_params)

        # Save to CSV
        csv_path = scraper.save_to_csv(output_path)

        # Save to Google Sheets if requested
        google_sheets_success = False
        if google_sheet_id:
            google_sheets_success = scraper.save_to_google_sheets(google_sheet_id)

        # Log completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Create log entry
        log_entry = {
            'timestamp': end_time.isoformat(),
            'leads_found': len(leads),
            'duration_seconds': duration,
            'output_path': csv_path,
            'google_sheets_upload': google_sheets_success,
            'search_params': search_params or {},
            'max_records': max_records
        }

        # Save log
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "lead_extraction_log.txt")

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{json.dumps(log_entry)}\n")

        logger.info(f"Scrape completed successfully. Found {len(leads)} leads in {duration:.2f} seconds")

        return {
            'success': True,
            'leads_count': len(leads),
            'output_path': csv_path,
            'log_entry': log_entry,
            'leads_data': leads
        }

    except Exception as e:
        logger.error(f"Error during scraping: {e}")

        # Log error
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'search_params': search_params or {},
            'max_records': max_records
        }

        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "lead_extraction_log.txt")

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"ERROR: {json.dumps(error_entry)}\n")

        return {
            'success': False,
            'error': str(e),
            'leads_count': 0,
            'log_entry': error_entry
        }


if __name__ == "__main__":
    # Test the scraper
    result = scrape_realtor_directory(
        output_path="outputs/test_realtor_leads.csv",
        max_records=10,
        verbose=True
    )

    print(f"Scraping result: {result}")
