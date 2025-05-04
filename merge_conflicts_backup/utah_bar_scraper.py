"""
Final Merged Utah State Bar Directory Scraper
Includes iframe handling, dynamic retries, concurrency, and profile detail scraping.
Improved with robust selectors, exception handling, CAPTCHA detection, anti-block headers.
"""

import argparse
import csv
import logging
import os
import random
import re
import time
<<<<<<< HEAD
from datetime import datetime
from typing import Callable
=======
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Callable, Dict, List, Optional
>>>>>>> 3ccf4fd (Committing all changes)

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UtahBarScraper:
"""TODO: Add docstring."""
    def __init__(self, headless=True, max_pages=50, retry_attempts=3, user_agent=None, workers=1):
    """TODO: Add docstring."""
        self.headless = headless
        self.max_pages = max_pages
        self.retry_attempts = retry_attempts
        self.user_agent = user_agent
        self.results = []
        self.workers = workers
        self.base_url = "https://services.utahbar.org/Member-Directory"

        self._load_env()
        self._setup_dirs()
        self.logger = self._setup_logger()

    def _load_env(self):
    """TODO: Add docstring."""
        env_file = ".env.work" if "samq" in os.getcwd().lower() else ".env"
        env_path = os.path.join(
            "C:/Users/samq/OneDrive - Digital Age Marketing Group/Desktop/Local Py",
            env_file,
        )
        load_dotenv(env_path)
        self.chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
        if not self.chromedriver_path or not os.path.exists(self.chromedriver_path):
            raise ValueError(f"Invalid CHROMEDRIVER_PATH: {self.chromedriver_path}")

    def _setup_dirs(self):
    """TODO: Add docstring."""
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, "data")
        self.log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def _setup_logger(self):
    """TODO: Add docstring."""
        logger = logging.getLogger("UtahBarScraper")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers():
            logger.handlers.clear()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fh = logging.FileHandler(os.path.join(self.log_dir, f"scraper_{timestamp}.log"))
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def setup_driver(self):
    """TODO: Add docstring."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        if self.user_agent:
            options.add_argument(f"user-agent={self.user_agent}")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=options)
        try:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd(
                "Network.setExtraHTTPHeaders",
<<<<<<< HEAD
                {
                    "Referer": "https://www.utahbar.org/",
                    "X-Requested-With": "XMLHttpRequest",
                },
=======
                {"Referer": "https://www.utahbar.org/", "X-Requested-With": "XMLHttpRequest"},
>>>>>>> 3ccf4fd (Committing all changes)
            )
        except Exception as e:
            self.logger.warning(f"Failed to set custom headers: {e}")
        return driver

    def with_retry(self, func: Callable, *args, **kwargs):
    """TODO: Add docstring."""
        for attempt in range(self.retry_attempts):
            try:
                return func(*args, **kwargs)
            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                self.logger.warning(f"Retry {attempt+1}/{self.retry_attempts} failed: {e}")
                time.sleep(random.uniform(2, 5))
        return None

    def switch_to_iframe(self, driver):
    """TODO: Add docstring."""
        try:
            iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            return True
        except Exception as e:
            self.logger.warning(f"Iframe not found: {e}")
            return False

    def perform_search(self, driver):
    """TODO: Add docstring."""
        driver.get(self.base_url)
        self.switch_to_iframe(driver)
        try:
            search_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id^='search-btn']"))
            )
            driver.execute_script("arguments[0].click();", search_btn)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            return True
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return False

    def extract_table_rows(self, driver):
    """TODO: Add docstring."""
        results = []
        try:
            rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 5:
                    continue
                profile_link = (
                    cells[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                    if cells[1].find_elements(By.TAG_NAME, "a")
                    else "N/A"
                )
                result = {
                    "BarNumber": cells[0].text.strip(),
                    "Name": cells[1].text.strip(),
                    "Organization": cells[2].text.strip(),
                    "Type": cells[3].text.strip(),
                    "Status": cells[4].text.strip(),
                    "ProfileLink": profile_link,
                }
                if self.validate_profile(result):
                    if "Inactive" in result["Status"]:
                        self.logger.info(f"Skipping inactive member: {result['Name']}")
                        continue
                    results.append(result)
        except Exception as e:
            self.logger.warning(f"Row extraction error: {e}")
        return results

    def validate_profile(self, profile):
<<<<<<< HEAD
=======
    """TODO: Add docstring."""
>>>>>>> 3ccf4fd (Committing all changes)
        return re.match(r"^\\d{6}$", profile.get("BarNumber", "")) and all(profile.get(k) for k in ["Name", "Status"])

    def go_to_next_page(self, driver, current_page):
    """TODO: Add docstring."""
        try:
            time.sleep(random.uniform(1.2, 3.8))
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Next')]"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            return True
        except Exception:
            return False

    def scrape(self):
    """TODO: Add docstring."""
        driver = self.setup_driver()
        try:
            if not self.with_retry(self.perform_search, driver):
                return
            page = 1
            while page <= self.max_pages:
                self.logger.info(f"Scraping page {page}")
                data = self.with_retry(self.extract_table_rows, driver)
                if data:
                    self.results.extend(data)
                if not self.with_retry(self.go_to_next_page, driver, page):
                    break
                page += 1
        finally:
            driver.quit()
        self.save_csv()

    def save_csv(self):
    """TODO: Add docstring."""
        if not self.results:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.data_dir, f"utah_bar_results_{timestamp}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)
        self.logger.info(f"Saved {len(self.results)} entries to {path}")


def parse_args():
"""TODO: Add docstring."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--retry", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scraper = UtahBarScraper(
<<<<<<< HEAD
        headless=args.headless,
        max_pages=args.max_pages,
        retry_attempts=args.retry,
        workers=args.workers,
=======
        headless=args.headless, max_pages=args.max_pages, retry_attempts=args.retry, workers=args.workers
>>>>>>> 3ccf4fd (Committing all changes)
    )
    scraper.scrape()
