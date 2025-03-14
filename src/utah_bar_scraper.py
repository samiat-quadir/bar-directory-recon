#!/usr/bin/env python3
# utah_bar_scraper_final.py

import os
import time
import json
import csv
import random
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# ✅ Load Environment Variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# ✅ Configuration & Argument Parsing
parser = argparse.ArgumentParser(description="Scrape Utah State Bar Directory")
parser.add_argument('--headless', action='store_true', help='Run in headless mode')
parser.add_argument('--max-pages', type=int, default=50, help='Max number of pages to scrape')
parser.add_argument('--get-details', action='store_true', help='Scrape detailed profiles')
args = parser.parse_args()

# ✅ Load Dynamic Paths
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Logging Setup
LOG_FILENAME = os.path.join(LOG_DIR, f"utah_bar_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=LOG_FILENAME, filemode="a", format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

def log_info(message):
    logging.info(message)
    print(f"[INFO] {message}")

def log_error(message):
    logging.error(message)
    print(f"[ERROR] {message}")

# ✅ Setup Web Driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    if args.headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ✅ Perform Search Before Scraping
def perform_search(driver):
    try:
        log_info("Performing search to load all attorney records...")
        search_button_xpath = "/html/body/div[3]/div[2]/div/form/div/button[1]"
        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, search_button_xpath))
        )
        search_button.click()
        time.sleep(5)
        return True
    except TimeoutException:
        log_error("Search button not found. Page structure may have changed.")
        return False

# ✅ Extract Data From Directory Table
def extract_table_rows(driver):
    try:
        # ✅ UPDATED: Use alternative XPath if needed
        table_xpath_variants = [
            "/html/body/div[3]/div[2]/div/table/tbody/tr",  # Old XPath
            "//table[contains(@class, 'directory-table')]/tbody/tr"  # Possible new XPath
        ]
        rows = None
        for xpath in table_xpath_variants:
            try:
                rows = driver.find_elements(By.XPATH, xpath)
                if rows:
                    log_info(f"Table found with XPath: {xpath}")
                    break
            except NoSuchElementException:
                continue
        if not rows:
            log_error("Table rows not found. Page structure may have changed.")
            return []

        results = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 5:
                continue
            result = {
                "BarNumber": cells[0].text.strip(),
                "Name": cells[1].text.strip(),
                "Organization": cells[2].text.strip(),
                "Type": cells[3].text.strip(),
                "Status": cells[4].text.strip(),
                "ProfileLink": "N/A"
            }
            links = cells[1].find_elements(By.TAG_NAME, "a")
            if links:
                result["ProfileLink"] = links[0].get_attribute("href") or "N/A"
            results.append(result)
        log_info(f"Extracted {len(results)} rows from table.")
        return results
    except NoSuchElementException:
        log_error("Table rows not found. Website may have changed.")
        return []

# ✅ Navigate to Next Page
def navigate_next_page(driver, current_page):
    try:
        next_button_xpath = "/html/body/div[3]/div[2]/div/div[3]/span[3]/a"
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_button_xpath))
        )
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)
        return True
    except (TimeoutException, NoSuchElementException):
        log_info(f"No more pages to scrape after page {current_page}.")
        return False

# ✅ Scrape Data Function
def scrape_data():
    driver = setup_driver()
    driver.get("https://services.utahbar.org/Member-Directory")

    if not perform_search(driver):
        driver.quit()
        return

    all_results = []
    page = 1
    while page <= args.max_pages:
        log_info(f"Scraping page {page}")
        time.sleep(random.uniform(2, 4))
        page_results = extract_table_rows(driver)
        all_results.extend(page_results)

        if not navigate_next_page(driver, page):
            break
        page += 1

    driver.quit()
    save_results(all_results)

# ✅ Save Results to CSV
def save_results(data):
    csv_path = os.path.join(DATA_DIR, f"utah_bar_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    log_info(f"Saved {len(data)} records to {csv_path}")

# ✅ Reattempt Failed Profiles
def reprocess_failed_profiles():
    if not os.path.exists("failed_profiles.json"):
        log_info("No failed profiles to reprocess.")
        return

    with open("failed_profiles.json", "r") as f:
        profiles = json.load(f)

    if not profiles:
        log_info("Failed profiles list is empty.")
        return

    log_info(f"Reprocessing {len(profiles)} failed profiles.")
    driver = setup_driver()
    reprocessed = []
    for profile in profiles:
        profile["Reattempted"] = True
        reprocessed.append(profile)

    driver.quit()
    with open("failed_profiles.json", "w") as f:
        json.dump(reprocessed, f)
    log_info("Updated failed_profiles.json.")

if __name__ == "__main__":
    scrape_data()
    reprocess_failed_profiles()
