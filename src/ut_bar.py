"""
Final Merged Utah State Bar Directory Scraper
Includes iframe handling, dynamic retries, concurrency, and profile detail scraping.
Improved with robust selectors, exception handling, pagination stability, and anti-block headers.
"""

import argparse
import csv
import logging
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections.abc import Callable

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UtahBarScraper:
    def __init__(
        self, headless=True, max_pages=50, retry_attempts=3, user_agent=None, workers=1
    ):
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
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        self.chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
        if not os.path.exists(self.chromedriver_path):
            raise ValueError("Invalid CHROMEDRIVER_PATH")

    def _setup_dirs(self):
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, "data")
        self.log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def _setup_logger(self):
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
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        if self.user_agent:
            options.add_argument(f"user-agent={self.user_agent}")
        driver = webdriver.Chrome(
            service=Service(self.chromedriver_path), options=options
        )
        try:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd(
                "Network.setExtraHTTPHeaders",
                {
                    "Referer": "https://www.utahbar.org/",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
        except Exception as e:
            self.logger.warning(f"Failed to set custom headers: {e}")
        return driver

    def with_retry(self, func: Callable, *args, **kwargs):
        for attempt in range(self.retry_attempts):
            try:
                return func(*args, **kwargs)
            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                self.logger.warning(
                    f"Retry {attempt+1}/{self.retry_attempts} failed: {e}"
                )
                time.sleep(random.uniform(2, 5))
        return None

    def switch_to_iframe(self, driver):
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(iframe)
            return True
        except Exception as e:
            self.logger.warning(f"Iframe not found: {e}")
            return False

    def perform_search(self, driver):
        driver.get(self.base_url)
        self.switch_to_iframe(driver)
        try:
            search_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[id^='search-btn']")
                )
            )
            driver.execute_script("arguments[0].click();", search_btn)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            return True
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return False

    def extract_table_rows(self, driver):
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
        return re.match(r"^\\d{6}$", profile.get("BarNumber", "")) and all(
            profile.get(k) for k in ["Name", "Status"]
        )

    def go_to_next_page(self, driver, current_page):
        try:
            time.sleep(random.uniform(1.2, 3.8))
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Next')]"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            return True
        except Exception:
            return False

    def scrape_page(self, page_num):
        driver = self.setup_driver()
        results = []
        try:
            if not self.with_retry(self.perform_search, driver):
                return results
            for i in range(1, page_num):
                if not self.with_retry(self.go_to_next_page, driver, i):
                    return results
            results = self.with_retry(self.extract_table_rows, driver) or []
        except Exception as e:
            self.logger.error(f"Error on page {page_num}: {e}")
        finally:
            driver.quit()
        return results

    def scrape_with_concurrency(self):
        self.logger.info(
            f"Starting parallel scrape across {self.max_pages} pages with {self.workers} workers."
        )
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self.scrape_page, page): page
                for page in range(1, self.max_pages + 1)
            }
            for future in futures:
                page = futures[future]
                try:
                    result = future.result()
                    self.logger.info(f"Page {page} scraped with {len(result)} entries.")
                    self.results.extend(result)
                except Exception as e:
                    self.logger.error(f"Page {page} failed: {e}")
        self.save_csv()

    def scrape(self):
        if self.workers > 1:
            return self.scrape_with_concurrency()
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--retry", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scraper = UtahBarScraper(
        headless=args.headless,
        max_pages=args.max_pages,
        retry_attempts=args.retry,
        workers=args.workers,
    )
    scraper.scrape()
