#!/usr/bin/env python3
# utah_bar_scraper.py

import os
import time
import csv
import json
import argparse
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException
)
from selenium.webdriver import ActionChains

########################################
# GLOBAL CONFIG & LOGGING SETUP
########################################

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scrape Utah Bar Member Directory')
parser.add_argument('--blank-search', action='store_true', 
                    help='Perform a blank search to get all records (default: search for "and~")')
parser.add_argument('--headless', action='store_true',
                    help='Run in headless mode (no browser UI)')
parser.add_argument('--max-pages', type=int, default=999,
                    help='Maximum number of pages to scrape (default: 999)')
parser.add_argument('--start-page', type=int, default=1,
                    help='Page to start scraping from (default: 1)')
parser.add_argument('--get-details', action='store_true',
                    help='Click into each profile to get detailed information')
parser.add_argument('--ignore-checkpoint', action='store_true',
                    help='Ignore existing checkpoint and start from beginning')
parser.add_argument('--skip-details', action='store_true',
                    help='Skip collecting detailed profile information (faster)')
args = parser.parse_args()

# Adjust this path to point to your local ChromeDriver
CHROMEDRIVER_PATH = r"C:\Users\samq\Downloads\chromedriver-win64 (2)\chromedriver-win64\chromedriver.exe"

# Active status filters - attorneys with these statuses will be included
ACTIVE_STATUSES = ["Active", "Active Atty", "Active Attorney", "Active Attny", "Active Mem"]

# Load config.json if available; otherwise, use defaults
CONFIG = {}
try:
    with open("config.json", "r", encoding="utf-8") as conf:
        CONFIG = json.load(conf)
except FileNotFoundError:
    CONFIG = {
        "global_settings": {
            "proxy_enabled": False,
            "stealth_mode": True,
            "request_timeout": 30
        }
    }

# Setup logging
os.makedirs("logs", exist_ok=True)
timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILENAME = os.path.join("logs", f"utah_bar_scraper_{timestamp_str}.log")
logging.basicConfig(
    filename=LOG_FILENAME,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(console_handler)

def log_error(msg: str) -> None:
    logging.error(msg)
    print(f"[ERROR] {msg}")

def log_info(msg: str) -> None:
    logging.info(msg)
    print(f"[INFO] {msg}")

########################################
# WEBDRIVER SETUP
########################################

def setup_webdriver(headless=False) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--use-angle=swiftshader")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    if CONFIG["global_settings"].get("stealth_mode", False):
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1920, 1080)
        return driver
    except Exception as e:
        log_error(f"Failed to create WebDriver: {str(e)}")
        raise

def restart_browser(driver):
    log_info("Attempting to restart browser")
    try:
        driver.quit()
    except:
        pass
    new_driver = setup_webdriver(headless=args.headless)
    log_info("Browser restarted successfully")
    return new_driver

########################################
# IFRAME AND FORM HANDLING
########################################

def diagnose_page_structure(driver):
    log_info("Diagnosing page structure...")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    log_info(f"Found {len(iframes)} iframes on page")
    for idx, iframe in enumerate(iframes):
        iframe_id = iframe.get_attribute("id") or "no-id"
        iframe_name = iframe.get_attribute("name") or "no-name"
        iframe_src = iframe.get_attribute("src") or "no-src"
        log_info(f"  Iframe #{idx}: id='{iframe_id}', name='{iframe_name}', src='{iframe_src}'")
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    driver.save_screenshot(f"screenshots/page_structure_{timestamp}.png")
    os.makedirs("debug", exist_ok=True)
    with open(f"debug/page_source_{timestamp}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

def switch_to_main_content(driver):
    try:
        driver.switch_to.default_content()
        return True
    except Exception as e:
        log_error(f"Error switching to main content: {str(e)}")
        return False

def find_and_switch_iframe(driver, max_retries=3):
    switch_to_main_content(driver)
    for retry in range(max_retries):
        try:
            known_iframe_id = "dnn_ctr423_IFrame_htmIFrame"
            try:
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, known_iframe_id))
                )
                log_info(f"Found iframe with ID: {known_iframe_id}")
                driver.switch_to.frame(iframe)
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    return True
                except:
                    if retry < max_retries - 1:
                        log_info("Switched to iframe but couldn't verify content, retrying...")
                        time.sleep(2)
                        switch_to_main_content(driver)
                        continue
                    log_info("Switched to iframe but no content access")
                    switch_to_main_content(driver)
            except:
                log_info(f"Iframe with ID '{known_iframe_id}' not found")
            if retry == 0:
                diagnose_page_structure(driver)
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for idx, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    log_info(f"Switched to iframe #{idx}")
                    body = driver.find_elements(By.TAG_NAME, "body")
                    if body and len(body[0].text.strip()) > 20:
                        log_info(f"Found content in iframe #{idx}")
                        return True
                    driver.switch_to.default_content()
                except Exception as e:
                    log_error(f"Error with iframe #{idx}: {str(e)}")
                    driver.switch_to.default_content()
            if retry < max_retries - 1:
                log_info(f"Retrying iframe search in {(retry+1)*2} seconds...")
                time.sleep((retry+1)*2)
                driver.refresh()
                time.sleep(3)
                continue
        except Exception as e:
            log_error(f"Iframe search error (attempt {retry+1}): {str(e)}")
            if retry < max_retries - 1:
                time.sleep((retry+1)*2)
                continue
    log_error(f"Could not find suitable iframe after {max_retries} attempts")
    return False

def ensure_iframe_context(driver, max_retries=3):
    for retry in range(max_retries):
        try:
            driver.find_element(By.TAG_NAME, "table")
            return True
        except:
            log_info(f"Lost iframe context, attempting recovery (attempt {retry+1}/{max_retries})")
            switch_to_main_content(driver)
            if find_and_switch_iframe(driver):
                return True
            elif retry < max_retries - 1:
                log_info("Refreshing page for iframe recovery")
                driver.refresh()
                time.sleep(3+retry)
                continue
    log_error(f"Failed to recover iframe context after {max_retries} attempts")
    return False

def perform_member_search(driver, blank_search=False, max_retries=3):
    for retry in range(max_retries):
        try:
            if blank_search:
                log_info("Performing blank search to get all records")
            else:
                last_name_selectors = [
                    "input[name='LastName']",
                    "input[name='txtLastName']", 
                    "input#txtLastName",
                    "input[placeholder*='Last']",
                    "input[id$='Last_Name']",
                    "input.form-control[id*='Last']"
                ]
                last_name_field = None
                for selector in last_name_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                last_name_field = element
                                element.clear()
                                element.send_keys("and~")
                                log_info(f"Entered 'and~' in field: {selector}")
                                break
                        if last_name_field:
                            break
                    except:
                        continue
                if not last_name_field and not blank_search:
                    log_info("Could not find specific Last Name field")
            button_selectors = [
                "input[type='submit'][value='Search']",
                "button[type='submit']",
                "input[type='submit']",
                "button.btn-primary",
                "input[value='Search']"
            ]
            button_found = False
            for selector in button_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed():
                            button_text = button.text.lower() if button.text else ""
                            button_value = button.get_attribute("value") or ""
                            if "search" in button_text or "search" in button_value.lower() or not button_text:
                                os.makedirs("screenshots/search", exist_ok=True)
                                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                                driver.save_screenshot(f"screenshots/search/before_click_{ts}.png")
                                try:
                                    driver.execute_script("arguments[0].click();", button)
                                except:
                                    try:
                                        button.click()
                                    except:
                                        actions = ActionChains(driver)
                                        actions.move_to_element(button).click().perform()
                                log_info(f"Clicked button: {selector} with text: {button_text}")
                                time.sleep(5)
                                driver.save_screenshot(f"screenshots/search/after_click_{ts}.png")
                                try:
                                    WebDriverWait(driver, 15).until(
                                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                                    )
                                    button_found = True
                                    break
                                except TimeoutException:
                                    if retry < max_retries - 1:
                                        log_info("Search button clicked but no results, retrying...")
                                        continue
                                    else:
                                        log_error("Search clicked but no results after retries")
                                        return False
                    if button_found:
                        break
                except:
                    continue
            if not button_found and retry < max_retries - 1:
                log_info(f"Could not find search button, retrying (attempt {retry+1}/{max_retries})")
                driver.refresh()
                time.sleep(3)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during search retry")
                    if retry == max_retries - 1:
                        return False
                continue
            elif not button_found:
                log_error("Could not find a suitable search button after retries")
                driver.save_screenshot("screenshots/no_search_button.png")
                return False
            return True
        except Exception as ex:
            log_error(f"Search execution failed (attempt {retry+1}): {str(ex)}")
            if retry < max_retries - 1:
                log_info(f"Retrying search in {(retry+1)*2} seconds...")
                time.sleep((retry+1)*2)
                driver.refresh()
                time.sleep(3)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during search retry")
                    if retry == max_retries - 1:
                        return False
                continue
            else:
                driver.save_screenshot("screenshots/search_failed.png")
                return False
    return False

########################################
# RESULTS EXTRACTION
########################################

def is_active_attorney(status):
    if not status or status == "Not available":
        return False
    for active_status in ACTIVE_STATUSES:
        if active_status.lower() in status.lower():
            return True
    inactive_keywords = ["deceased", "disbarred", "inactive", "resigned", "retired", "suspended", "surrendered"]
    for keyword in inactive_keywords:
        if keyword.lower() in status.lower():
            return False
    return True

def extract_search_results(driver, current_page=1, max_retries=5):
    results = []
    log_info(f"Extracting search results from page {current_page}...")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/results_page{current_page}_{ts}.png")
    for retry in range(max_retries):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            log_info("Found results table")
            rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
            log_info(f"Found {len(rows)} rows in results table")
            active_count = 0
            skipped_count = 0
            for row_idx, row in enumerate(rows):
                for row_retry in range(3):
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 5:
                            bar_number = cells[0].text.strip()
                            name = cells[1].text.strip()
                            organization = cells[2].text.strip()
                            attorney_type = cells[3].text.strip()
                            status = cells[4].text.strip()
                            admission_date = cells[5].text.strip() if len(cells) > 5 else "Not available"
                            if not is_active_attorney(status):
                                skipped_count += 1
                                break
                            active_count += 1
                            profile_link = None
                            try:
                                links = cells[1].find_elements(By.TAG_NAME, "a")
                                if links:
                                    profile_link = links[0].get_attribute("href")
                                    if not profile_link:
                                        profile_link = driver.execute_script("return arguments[0].href;", links[0])
                            except Exception as ex:
                                log_error(f"Error extracting profile link: {str(ex)}")
                            result = {
                                "BarNumber": bar_number,
                                "Name": name,
                                "Organization": organization,
                                "Type": attorney_type,
                                "Status": status,
                                "Bar Admission Date": admission_date,
                                "Email": "Not available",
                                "City": "Not available",
                                "Address": "Not available",
                                "ProfileLink": profile_link if profile_link else "Not available"
                            }
                            results.append(result)
                            break
                    except StaleElementReferenceException:
                        if row_retry < 2:
                            log_info(f"Stale element for row {row_idx+1}, retrying...")
                            rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
                            if row_idx < len(rows):
                                row = rows[row_idx]
                                time.sleep(0.5)
                                continue
                            else:
                                log_error(f"Row index {row_idx} out of bounds after refresh")
                                break
                        else:
                            log_error(f"Max retries reached for row {row_idx+1}, skipping")
                    except Exception as ex:
                        log_error(f"Error extracting data from row {row_idx+1}: {str(ex)}")
                        break
            log_info(f"Extracted {active_count} active attorneys from page {current_page}")
            log_info(f"Skipped {skipped_count} non-active attorneys on page {current_page}")
            if len(results) == 0 and retry < max_retries - 1:
                log_info(f"No results extracted from page {current_page}, retrying ({retry+1}/{max_retries})...")
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during results extraction retry")
                time.sleep(2)
                continue
            return results
        except StaleElementReferenceException:
            if retry < max_retries - 1:
                log_info(f"Stale element reference when extracting results, retrying ({retry+1}/{max_retries})...")
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during results extraction retry")
                time.sleep(2)
                continue
            else:
                log_error("Max retries reached for stale element during results extraction")
        except Exception as ex:
            log_error(f"Error extracting results from table: {str(ex)}")
            if retry < max_retries - 1:
                log_info(f"Retrying results extraction ({retry+1}/{max_retries})...")
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during results extraction retry")
                time.sleep(2)
                continue
    return results

def extract_email_from_text(text):
    if not text:
        return None
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_city_from_address(address_text):
    if not address_text or address_text == "Not available":
        return None
    lines = address_text.split('\n')
    if len(lines) >= 2:
        city_line = lines[1]
        if ',' in city_line:
            return city_line.split(',')[0].strip()
    for line in lines:
        if ',' in line and any(state in line for state in [' UT ', ' Utah ', ' ID ', ' AZ ', ' NV ']):
            return line.split(',')[0].strip()
    return None

def process_profile_page(driver, result, max_retries=3):
    profile_link = result.get("ProfileLink", "Not available")
    if profile_link == "Not available":
        log_info(f"No profile link available for {result['Name']}")
        return result
    log_info(f"Processing profile for {result['Name']} (Bar #{result['BarNumber']})")
    original_window = driver.current_window_handle
    windows_before = driver.window_handles
    for retry in range(max_retries):
        try:
            if retry > 0:
                log_info(f"Retry {retry}/{max_retries} for profile {result['Name']}")
                if len(driver.window_handles) > len(windows_before):
                    for window in driver.window_handles:
                        if window != original_window:
                            driver.switch_to.window(window)
                            driver.close()
                    driver.switch_to.window(original_window)
            if retry == 0:
                driver.execute_script(f"window.open('{profile_link}');")
                new_window = [w for w in driver.window_handles if w not in windows_before][0]
                driver.switch_to.window(new_window)
            else:
                driver.get(profile_link)
            time.sleep(3 + retry)
            try:
                iframe = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )
                driver.switch_to.frame(iframe)
                log_info("Switched to iframe in profile page")
            except:
                log_info("No iframe found on profile page, continuing")
            email_found = False
            email_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
            if email_elements:
                for elem in email_elements:
                    email = elem.get_attribute("href")
                    if email and email.startswith("mailto:"):
                        result["Email"] = email.replace("mailto:", "")
                        log_info(f"Found email via mailto: {result['Email']}")
                        email_found = True
                        break
            if not email_found:
                email_containers = driver.find_elements(By.XPATH, "//td[contains(text(), '@')] | //div[contains(text(), '@')] | //p[contains(text(), '@')]")
                for elem in email_containers:
                    extracted_email = extract_email_from_text(elem.text)
                    if extracted_email:
                        result["Email"] = extracted_email
                        log_info(f"Found email via text pattern: {result['Email']}")
                        email_found = True
                        break
            address_found = False
            address_selectors = [
                "//td[contains(text(), 'Mailing Address')]/following-sibling::td",
                "//td[contains(text(), 'Address')]/following-sibling::td",
                "//div[contains(text(), 'Mailing Address')]/following-sibling::div",
                "//div[contains(text(), 'Address')]/following-sibling::div",
                "//label[contains(text(), 'Address')]/following-sibling::*",
                "//h3[contains(text(), 'Address')]/following-sibling::*"
            ]
            for selector in address_selectors:
                try:
                    address_elements = driver.find_elements(By.XPATH, selector)
                    for elem in address_elements:
                        address_text = elem.text.strip()
                        if address_text and len(address_text) > 10:
                            result["Address"] = address_text
                            log_info(f"Found address using selector '{selector}'")
                            extracted_city = extract_city_from_address(address_text)
                            if extracted_city:
                                result["City"] = extracted_city
                                log_info(f"Extracted city: {result['City']}")
                            address_found = True
                            break
                    if address_found:
                        break
                except Exception as ex:
                    log_error(f"Error extracting address with selector '{selector}': {str(ex)}")
                    continue
            if result["City"] == "Not available" and result["Address"] != "Not available":
                try:
                    city_pattern = r'([A-Za-z\s.]+),\s*(?:UT|Utah|ID|Idaho|AZ|Arizona|NV|Nevada)'
                    city_matches = re.findall(city_pattern, result["Address"])
                    if city_matches:
                        result["City"] = city_matches[0].strip()
                        log_info(f"Extracted city using regex: {result['City']}")
                except Exception as ex:
                    log_error(f"Error extracting city with regex: {str(ex)}")
            screenshot_dir = os.path.join("screenshots", "profiles")
            os.makedirs(screenshot_dir, exist_ok=True)
            ts_profile = datetime.now().strftime("%Y%m%d%H%M%S")
            driver.save_screenshot(f"{screenshot_dir}/profile_{result['BarNumber']}_{ts_profile}.png")
            if retry == 0:
                driver.close()
                driver.switch_to.window(original_window)
            return result
        except Exception as ex:
            log_error(f"Error processing profile for {result['Name']} (attempt {retry+1}): {str(ex)}")
            try:
                if len(driver.window_handles) > len(windows_before):
                    for window in driver.window_handles:
                        if window != original_window:
                            driver.switch_to.window(window)
                            driver.close()
                    driver.switch_to.window(original_window)
            except Exception as cleanup_ex:
                log_error(f"Cleanup error after profile processing failure: {str(cleanup_ex)}")
                if retry == max_retries - 1:
                    log_info("Attempting browser restart after profile failure")
                    try:
                        driver.quit()
                        driver = restart_browser(driver)
                        return result
                    except:
                        log_error("Failed to restart browser")
                        return result
    return result

def process_pages_with_details(driver, base_url, max_pages):
    current_page = args.start_page
    all_results = []
    retry_count = 0
    max_retries = 5
    if current_page == 1 and not args.ignore_checkpoint:
        checkpoint = load_checkpoint()
        if checkpoint:
            current_page = checkpoint["last_page"] + 1
            log_info(f"Resuming from checkpoint: starting at page {current_page}")
            if current_page > 1:
                if not full_recovery(driver, current_page):
                    log_error("Failed to recover to checkpoint page")
                    return []
    while current_page <= max_pages:
        try:
            log_info(f"Processing page {current_page}")
            if not ensure_iframe_context(driver):
                log_info("Lost iframe context, refreshing page")
                driver.refresh()
                time.sleep(5)
                if not find_and_switch_iframe(driver):
                    retry_count += 1
                    if retry_count >= max_retries:
                        log_error("Failed to recover iframe context after retries")
                        break
                    continue
            page_results = extract_search_results(driver, current_page)
            if not page_results or len(page_results) == 0:
                retry_count += 1
                log_error(f"No results found on page {current_page}, attempt {retry_count}/{max_retries}")
                if retry_count >= max_retries:
                    if retry_count == max_retries and full_recovery(driver, current_page):
                        retry_count = 0
                        continue
                    else:
                        log_error(f"Failed after {max_retries} attempts, stopping")
                        break
                driver.refresh()
                time.sleep(5)
                find_and_switch_iframe(driver)
                continue
            log_info(f"Found {len(page_results)} results on page {current_page}")
            current_url = driver.current_url
            profiles_with_details = []
            for idx, result in enumerate(page_results):
                try:
                    log_info(f"Processing profile {idx+1}/{len(page_results)}: {result['Name']}")
                    detailed_result = process_profile_page(driver, result)
                    profiles_with_details.append(detailed_result)
                    driver.get(current_url)
                    time.sleep(3)
                    if not find_and_switch_iframe(driver):
                        log_error("Failed to switch back to iframe after profile")
                        if not full_recovery(driver, current_page):
                            break
                except Exception as ex:
                    log_error(f"Error processing profile {idx+1}: {str(ex)}")
                    profiles_with_details.append(result)
                    driver.get(current_url)
                    time.sleep(3)
                    find_and_switch_iframe(driver)
            all_results.extend(profiles_with_details)
            log_info(f"Processed {len(profiles_with_details)} profiles on page {current_page}")
            log_info(f"Total results so far: {len(all_results)}")
            save_checkpoint(current_page, len(all_results))
            retry_count = 0
            if check_for_pagination(driver):
                if navigate_to_next_page(driver, current_page):
                    current_page += 1
                    if current_page > max_pages:
                        log_info(f"Reached maximum page limit ({max_pages})")
                        break
                else:
                    retry_count += 1
                    log_error(f"Failed to navigate to next page, attempt {retry_count}/{max_retries}")
                    if retry_count >= max_retries:
                        if retry_count == max_retries and full_recovery(driver, current_page + 1):
                            current_page += 1
                            retry_count = 0
                            continue
                        else:
                            log_error(f"Failed after {max_retries} attempts, stopping")
                            break
                    driver.refresh()
                    time.sleep(5)
                    find_and_switch_iframe(driver)
                    continue
            else:
                log_info("No more pages found, finished pagination")
                break
        except Exception as ex:
            log_error(f"Error processing page {current_page}: {str(ex)}")
            retry_count += 1
            os.makedirs("screenshots/errors", exist_ok=True)
            ts_err = datetime.now().strftime("%Y%m%d%H%M%S")
            driver.save_screenshot(f"screenshots/errors/error_p{current_page}_{ts_err}.png")
            if retry_count >= max_retries:
                if retry_count == max_retries and full_recovery(driver, current_page):
                    retry_count = 0
                    continue
                else:
                    log_error(f"Failed after {max_retries} attempts, stopping pagination")
                    break
            driver.refresh()
            time.sleep(5 * retry_count)
            find_and_switch_iframe(driver)
            continue
    return all_results

def get_profile_details(driver, results):
    log_info(f"Starting detailed profile extraction for {len(results)} attorneys...")
    updated_results = []
    for idx, result in enumerate(results):
        bar_number = result["BarNumber"]
        name = result["Name"]
        profile_link = result.get("ProfileLink", "Not available")
        log_info(f"Processing detailed profile {idx+1}/{len(results)}: {name} (Bar #{bar_number})")
        try:
            if profile_link and profile_link != "Not available":
                driver.get(profile_link)
                log_info("Navigated directly to profile using stored link")
                time.sleep(3)
            else:
                log_info(f"No direct profile link for bar number {bar_number}, skipping")
                continue
            try:
                iframe = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )
                driver.switch_to.frame(iframe)
                log_info("Switched to iframe on profile page")
            except:
                log_info("No iframe found on profile page, continuing")
            email_found = False
            email_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
            if email_elements:
                for elem in email_elements:
                    email = elem.get_attribute("href")
                    if email and email.startswith("mailto:"):
                        result["Email"] = email.replace("mailto:", "")
                        log_info(f"Found email: {result['Email']}")
                        email_found = True
                        break
            if not email_found:
                email_containers = driver.find_elements(By.XPATH, 
                    "//td[contains(text(), '@')] | //div[contains(text(), '@')] | //p[contains(text(), '@')]")
                for elem in email_containers:
                    extracted_email = extract_email_from_text(elem.text)
                    if extracted_email:
                        result["Email"] = extracted_email
                        log_info(f"Found email via text: {result['Email']}")
                        email_found = True
                        break
            address_found = False
            address_selectors = [
                "//td[contains(text(), 'Mailing Address')]/following-sibling::td",
                "//td[contains(text(), 'Address')]/following-sibling::td",
                "//div[contains(text(), 'Mailing Address')]/following-sibling::div",
                "//div[contains(text(), 'Address')]/following-sibling::div",
                "//label[contains(text(), 'Address')]/following-sibling::*",
                "//h3[contains(text(), 'Address')]/following-sibling::*"
            ]
            for selector in address_selectors:
                try:
                    address_elements = driver.find_elements(By.XPATH, selector)
                    for elem in address_elements:
                        address_text = elem.text.strip()
                        if address_text and len(address_text) > 10:
                            result["Address"] = address_text
                            log_info(f"Found address with selector '{selector}'")
                            extracted_city = extract_city_from_address(address_text)
                            if extracted_city:
                                result["City"] = extracted_city
                                log_info(f"Extracted city: {result['City']}")
                            address_found = True
                            break
                    if address_found:
                        break
                except Exception as ex:
                    log_error(f"Error extracting address with '{selector}': {str(ex)}")
                    continue
            if result["City"] == "Not available" and result["Address"] != "Not available":
                try:
                    city_pattern = r'([A-Za-z\s.]+),\s*(?:UT|Utah|ID|Idaho|AZ|Arizona|NV|Nevada)'
                    city_matches = re.findall(city_pattern, result["Address"])
                    if city_matches:
                        result["City"] = city_matches[0].strip()
                        log_info(f"Extracted city using regex: {result['City']}")
                except Exception as ex:
                    log_error(f"Error extracting city with regex: {str(ex)}")
            screenshot_dir = os.path.join("screenshots", "profiles")
            os.makedirs(screenshot_dir, exist_ok=True)
            ts_prof = datetime.now().strftime("%Y%m%d%H%M%S")
            driver.save_screenshot(f"{screenshot_dir}/profile_{bar_number}_{ts_prof}.png")
        except Exception as ex:
            log_error(f"Error processing detailed profile for {name}: {str(ex)}")
        updated_results.append(result)
    log_info(f"Completed detailed extraction for {len(updated_results)} profiles.")
    return updated_results

########################################
# PAGINATION HANDLING
########################################

def check_for_pagination(driver):
    try:
        page_numbers = driver.find_elements(By.XPATH, "//a[string-length(text()) <= 3 and string(number(text())) != 'NaN']")
        if page_numbers and len(page_numbers) > 0:
            log_info(f"Found {len(page_numbers)} page number links")
            return True
        ellipsis = driver.find_elements(By.XPATH, "//a[contains(text(), '...')]")
        if ellipsis:
            log_info("Found pagination ellipsis")
            return True
        pagination_controls = driver.find_elements(By.XPATH, "//div[contains(@class, 'pag')] | //ul[contains(@class, 'pag')] | //nav[contains(@class, 'pag')]")
        if pagination_controls:
            log_info("Found pagination container")
            return True
        log_info("No pagination controls found")
        return False
    except Exception as ex:
        log_error(f"Error checking pagination: {str(ex)}")
        return False

def navigate_to_next_page(driver, current_page, max_attempts=5):
    next_page_num = current_page + 1
    wait_times = [2, 3, 5, 8, 13]
    for attempt in range(max_attempts):
        try:
            log_info(f"Navigation attempt {attempt+1}/{max_attempts} to page {next_page_num}")
            ts_nav = datetime.now().strftime("%Y%m%d%H%M%S")
            driver.save_screenshot(f"screenshots/pagination/before_nav_p{next_page_num}_a{attempt+1}_{ts_nav}.png")
            selectors = [
                f"//a[text()='{next_page_num}']",
                f"//a/span[text()='{next_page_num}']/..",
                f"//li/a[text()='{next_page_num}']",
                f"//ul[contains(@class, 'pagination')]//a[text()='{next_page_num}']",
                f"//div[contains(@class, 'pager')]//a[text()='{next_page_num}']",
                f"//a[contains(@href, 'page={next_page_num}')]"
            ]
            link_found = False
            for selector in selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and len(elements) > 0:
                    log_info(f"Found link to page {next_page_num} using: {selector}")
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elements[0])
                        time.sleep(1)
                    except:
                        log_info("Failed to scroll to pagination element")
                    try:
                        driver.execute_script("arguments[0].click();", elements[0])
                    except:
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(elements[0]).click().perform()
                        except:
                            elements[0].click()
                    time.sleep(3)
                    driver.save_screenshot(f"screenshots/pagination/after_nav_p{next_page_num}_a{attempt+1}_{ts_nav}.png")
                    active_indicators = driver.find_elements(By.XPATH, "//li[contains(@class, 'active')]/a")
                    if active_indicators:
                        for indicator in active_indicators:
                            if indicator.text.strip() == str(next_page_num):
                                log_info(f"Successfully navigated to page {next_page_num}")
                                return True
                    if len(driver.find_elements(By.XPATH, "//table//tr")) > 1:
                        log_info(f"Successfully navigated to page {next_page_num} (verified by table rows)")
                        return True
                    link_found = True
                    break
            if not link_found:
                next_selectors = [
                    "//a[contains(text(), 'Next')]",
                    "//a[contains(text(), 'next')]",
                    "//a[contains(text(), '>')]",
                    "//a[contains(text(), '»')]",
                    "//a[contains(@class, 'next')]",
                    "//a[contains(@rel, 'next')]",
                    "//a[contains(@aria-label, 'Next')]"
                ]
                for selector in next_selectors:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > 0:
                        log_info(f"Found 'Next' button using: {selector}")
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elements[0])
                            time.sleep(1)
                        except:
                            log_info("Failed to scroll to Next button")
                        try:
                            driver.execute_script("arguments[0].click();", elements[0])
                        except:
                            try:
                                actions = ActionChains(driver)
                                actions.move_to_element(elements[0]).click().perform()
                            except:
                                elements[0].click()
                        time.sleep(3)
                        driver.save_screenshot(f"screenshots/pagination/after_next_p{next_page_num}_a{attempt+1}_{ts_nav}.png")
                        if len(driver.find_elements(By.XPATH, "//table//tr")) > 1:
                            log_info("Successfully navigated using Next button")
                            return True
                        link_found = True
                        break
            if not link_found and navigate_by_url_params(driver, current_page):
                return True
            if attempt < max_attempts - 1:
                log_info(f"Navigation attempt {attempt+1} failed, refreshing context and retrying")
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe during navigation retry")
                wait_time = wait_times[attempt] if attempt < len(wait_times) else wait_times[-1]
                log_info(f"Waiting {wait_time} seconds before next attempt")
                time.sleep(wait_time)
                if attempt == max_attempts - 2:
                    log_info("Refreshing page before final attempt")
                    driver.refresh()
                    time.sleep(5)
                    find_and_switch_iframe(driver)
                continue
        except StaleElementReferenceException:
            log_info(f"Stale element encountered during navigation to page {next_page_num}")
            if attempt < max_attempts - 1:
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe after stale element")
                wait_time = wait_times[attempt] if attempt < len(wait_times) else wait_times[-1]
                log_info(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
                continue
        except Exception as ex:
            log_error(f"Error during navigation to page {next_page_num}: {str(ex)}")
            if attempt < max_attempts - 1:
                switch_to_main_content(driver)
                if not find_and_switch_iframe(driver):
                    log_error("Failed to switch to iframe after navigation error")
                wait_time = wait_times[attempt] if attempt < len(wait_times) else wait_times[-1]
                log_info(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
                continue
    log_error(f"Could not navigate to page {next_page_num} after {max_attempts} attempts")
    return False

def navigate_by_url_params(driver, current_page):
    try:
        next_page = current_page + 1
        current_url = driver.current_url
        log_info(f"Attempting URL navigation to page {next_page}")
        original_url = current_url
        if 'page=' in current_url:
            new_url = re.sub(r'page=\d+', f'page={next_page}', current_url)
        elif '/page/' in current_url:
            new_url = re.sub(r'/page/\d+/', f'/page/{next_page}/', current_url)
        else:
            if '?' in current_url:
                new_url = f"{current_url}&page={next_page}"
            else:
                new_url = f"{current_url}?page={next_page}"
        log_info(f"URL navigation to page {next_page}: {new_url}")
        ts_url = datetime.now().strftime("%Y%m%d%H%M%S")
        driver.save_screenshot(f"screenshots/url_nav_before_{ts_url}.png")
        driver.get(new_url)
        time.sleep(5)
        driver.save_screenshot(f"screenshots/url_nav_after_{ts_url}.png")
        if find_and_switch_iframe(driver):
            tables = driver.find_elements(By.TAG_NAME, "table")
            if tables and len(driver.find_elements(By.XPATH, "//table//tr")) > 1:
                log_info(f"Successfully navigated to page {next_page} via URL")
                return True
            else:
                log_info("URL navigation did not load a results table")
        else:
            log_info("URL navigation failed to find iframe")
        log_info("Returning to original URL")
        driver.get(original_url)
        time.sleep(3)
        find_and_switch_iframe(driver)
        return False
    except Exception as ex:
        log_error(f"Error navigating by URL parameters: {str(ex)}")
        return False

def full_recovery(driver, target_page, max_retries=3):
    log_info(f"Attempting full recovery to page {target_page}")
    for retry in range(max_retries):
        try:
            base_url = "https://services.utahbar.org/Member-Directory"
            driver.get(base_url)
            time.sleep(8)
            if not find_and_switch_iframe(driver):
                log_error(f"Failed to switch to iframe during recovery (attempt {retry+1})")
                if retry < max_retries - 1:
                    log_info(f"Retrying in {(retry+1)*3} seconds...")
                    time.sleep((retry+1)*3)
                    continue
                else:
                    return False
            if not perform_member_search(driver, blank_search=args.blank_search):
                log_error(f"Failed to execute search during recovery (attempt {retry+1})")
                if retry < max_retries - 1:
                    log_info(f"Retrying in {(retry+1)*3} seconds...")
                    time.sleep((retry+1)*3)
                    continue
                else:
                    return False
            time.sleep(10)
            current_page = 1
            while current_page < target_page:
                log_info(f"Recovery: navigating to page {current_page + 1}")
                if navigate_to_next_page(driver, current_page):
                    current_page += 1
                else:
                    log_error(f"Failed to reach page {target_page} during recovery (at page {current_page})")
                    if current_page >= target_page - 1:
                        log_info(f"Reached page {current_page}, close enough to target {target_page}")
                        return True
                    if retry < max_retries - 1:
                        log_info(f"Retrying full recovery in {(retry+1)*3} seconds...")
                        time.sleep((retry+1)*3)
                        break
                    else:
                        return False
            if current_page == target_page:
                log_info(f"Successfully recovered to page {target_page}")
                return True
        except Exception as ex:
            log_error(f"Error during full recovery (attempt {retry+1}): {str(ex)}")
            if retry < max_retries - 1:
                log_info(f"Retrying full recovery in {(retry+1)*3} seconds...")
                time.sleep((retry+1)*3)
            else:
                return False
    return False

########################################
# CHECKPOINTING
########################################

def save_checkpoint(page, results_count):
    checkpoint = {
        "last_page": page,
        "results_count": results_count,
        "timestamp": datetime.now().isoformat()
    }
    os.makedirs("checkpoints", exist_ok=True)
    with open("checkpoints/last_checkpoint.json", "w") as f:
        json.dump(checkpoint, f)
    log_info(f"Checkpoint saved: page {page}, {results_count} results")

def load_checkpoint():
    try:
        with open("checkpoints/last_checkpoint.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

########################################
# MAIN ENTRY POINT
########################################

def main():
    driver = setup_webdriver(headless=args.headless)
    start_time = time.time()
    all_results = []
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("data", exist_ok=True)
    filename_prefix = "active_attorneys" if args.blank_search else "active_search_results"
    csv_path = os.path.join("data", f"utah_bar_{filename_prefix}_{timestamp_str}.csv")
    try:
        base_url = "https://services.utahbar.org/Member-Directory"
        driver.get(base_url)
        log_info("Navigated to Utah Bar Member Directory")
        time.sleep(8)
        if not find_and_switch_iframe(driver):
            log_error("Failed to switch to iframe, cannot proceed")
            return
        search_success = perform_member_search(driver, blank_search=args.blank_search)
        if not search_success:
            log_error("Failed to execute search")
            return
        log_info("Search executed, waiting for results...")
        time.sleep(10)
        fieldnames = [
            "BarNumber", "Name", "Organization", "Type", "Status", 
            "Bar Admission Date", "Email", "City", "Address"
        ]
        if args.get_details and not args.skip_details:
            log_info("Starting detailed profile extraction for all pages")
            all_results = process_pages_with_details(driver, base_url, args.max_pages)
        else:
            current_page = args.start_page
            max_pages = args.max_pages
            retry_count = 0
            max_retries = 5
            if current_page == 1 and not args.ignore_checkpoint:
                checkpoint = load_checkpoint()
                if checkpoint:
                    current_page = checkpoint["last_page"] + 1
                    log_info(f"Resuming from checkpoint: starting at page {current_page}")
                    if current_page > 1:
                        if not full_recovery(driver, current_page):
                            log_error("Failed to recover to checkpoint page")
                            return
            while current_page <= max_pages:
                try:
                    log_info(f"Processing page {current_page}")
                    if not ensure_iframe_context(driver):
                        log_info("Lost iframe context, refreshing page")
                        driver.refresh()
                        time.sleep(5)
                        if not find_and_switch_iframe(driver):
                            retry_count += 1
                            if retry_count >= max_retries:
                                log_error("Failed to recover iframe context after retries")
                                break
                            continue
                    page_results = extract_search_results(driver, current_page)
                    if not page_results or len(page_results) == 0:
                        retry_count += 1
                        log_error(f"No results found on page {current_page}, attempt {retry_count}/{max_retries}")
                        if retry_count >= max_retries:
                            if retry_count == max_retries and full_recovery(driver, current_page):
                                retry_count = 0
                                continue
                            else:
                                log_error(f"Failed after {max_retries} attempts, stopping")
                                break
                        driver.refresh()
                        time.sleep(5)
                        find_and_switch_iframe(driver)
                        continue
                    all_results.extend(page_results)
                    log_info(f"Total results so far: {len(all_results)}")
                    save_checkpoint(current_page, len(all_results))
                    retry_count = 0
                    if check_for_pagination(driver):
                        if navigate_to_next_page(driver, current_page):
                            current_page += 1
                            if current_page > max_pages:
                                log_info(f"Reached maximum page limit ({max_pages})")
                                break
                        else:
                            retry_count += 1
                            log_error(f"Failed to navigate to next page, attempt {retry_count}/{max_retries}")
                            if retry_count >= max_retries:
                                if retry_count == max_retries and full_recovery(driver, current_page + 1):
                                    current_page += 1
                                    retry_count = 0
                                    continue
                                else:
                                    log_error(f"Failed after {max_retries} attempts, stopping")
                                    break
                            driver.refresh()
                            time.sleep(5)
                            find_and_switch_iframe(driver)
                            continue
                    else:
                        log_info("No more pages found, finished pagination")
                        break
                except Exception as ex:
                    log_error(f"Error processing page {current_page}: {str(ex)}")
                    retry_count += 1
                    os.makedirs("screenshots/errors", exist_ok=True)
                    ts_err = datetime.now().strftime("%Y%m%d%H%M%S")
                    driver.save_screenshot(f"screenshots/errors/error_p{current_page}_{ts_err}.png")
                    if retry_count >= max_retries:
                        if retry_count == max_retries and full_recovery(driver, current_page):
                            retry_count = 0
                            continue
                        else:
                            log_error(f"Failed after {max_retries} attempts, stopping pagination")
                            break
                    driver.refresh()
                    time.sleep(5 * retry_count)
                    find_and_switch_iframe(driver)
                    continue
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for result in all_results:
                if "ProfileLink" in result:
                    del result["ProfileLink"]
                writer.writerow(result)
        log_info(f"Finished scraping. Total results: {len(all_results)}")
        log_info(f"Results saved to {csv_path}")
    except Exception as exc:
        log_error(f"Critical error in main flow: {str(exc)}")
        ts_main = datetime.now().strftime("%Y%m%d%H%M%S")
        driver.save_screenshot(f"screenshots/main_flow_error_{ts_main}.png")
    finally:
        driver.quit()
        elapsed = time.time() - start_time
        print(f"Done. Elapsed time: {elapsed:.1f} seconds.")

if __name__ == "__main__":
    main()
