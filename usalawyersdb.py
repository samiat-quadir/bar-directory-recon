import logging
import os
import re
import time

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ==== Inline ENV LOADER ====
current_user = os.environ.get("USERNAME", "").lower()
if current_user == "samq":
    env_file = ".env.work"
elif current_user == "samqu":
    env_file = ".env.asus"
else:
    raise EnvironmentError(
        f"⚠️ Unknown user '{current_user}'. Cannot determine which .env file to load."
    )

env_path = os.path.join(os.path.dirname(__file__), env_file)
load_dotenv(dotenv_path=env_path)
print(f"✅ Loaded environment from {env_file}")

# ==== Logging Setup ====
LOG_DIR = os.path.join(os.getenv("LOCAL_GIT_REPO"), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "scraper.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("lawyer_scraper")

# ==== Config ====
CHROME_DRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
OUTPUT_FOLDER = os.path.join(LOG_DIR, "output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
BASE_URL = "https://uslawyersdb.com/"
WAIT_TIME = 15
PAGE_LOAD_WAIT = 5

# ==== WebDriver Setup ====
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless=new")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)


# ==== Helper Functions ====
def safe_click(xpath, timeout=WAIT_TIME):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        time.sleep(2)
        return True
    except Exception as e:
        logger.warning(f"Click failed on {xpath}: {str(e)}")
        return False


def get_element_text(xpath, default="N/A", timeout=WAIT_TIME):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except Exception as e:
        logger.error(f"Error getting text from {xpath}: {str(e)}")
        return default


def get_element_attribute(xpath, attribute, default="N/A", timeout=WAIT_TIME):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.get_attribute(attribute).strip()
    except Exception as e:
        logger.error(f"Error getting attribute '{attribute}' from {xpath}: {str(e)}")
        return default


def get_total_lawyers():
    try:
        count_text = get_element_text("/html/body/div[2]/div[1]/div/div/div[5]/div[3]")
        numbers = re.findall(r"\d+", count_text)
        return int(numbers[-1]) if numbers else 0
    except Exception as e:
        logger.error(f"Failed to get total lawyers: {str(e)}")
        return 0


def scrape_lawyer_profile():
    try:
        profile_data = {
            "Name": get_element_text("/html/body/div[2]/div[2]/div/div[1]"),
            "Email": get_element_text("/html/body/div[2]/div[2]/div/div[5]/div/div[1]/p[5]"),
            "City": get_element_text(
                "/html/body/div[2]/div[2]/div/div[5]/div/div[1]/p[2]/a[1]/span"
            ),
            "State": get_element_text("/html/body/div[2]/div[2]/div/div[5]/div/div[1]/p[2]/a[2]"),
            "Update Date": get_element_text("/html/body/div[2]/div[2]/div/div[5]/div/div[1]/p[6]"),
            "Practice Areas": get_element_text("/html/body/div[2]/div[2]/div/div[5]/div/div[1]/ul"),
            "Website": get_element_attribute(
                "/html/body/div[2]/div[2]/div/div[5]/div/div[1]/p[4]/a", "href"
            ),
        }
        if "Email:" in profile_data["Email"]:
            profile_data["Email"] = profile_data["Email"].split("Email:")[-1].strip()
        logger.info(f"Scraped: {profile_data['Name']}")
        return profile_data
    except Exception as e:
        logger.error(f"Error scraping profile: {str(e)}")
        return {}


def scrape_state_lawyers(practice_area, state_name):
    all_profiles = []
    total_lawyers = get_total_lawyers()
    logger.info(f"Total lawyers in {state_name}: {total_lawyers}")
    current_page = 1
    lawyers_scraped = 0
    while lawyers_scraped < total_lawyers:
        try:
            profile_links = driver.find_elements(
                By.XPATH, "/html/body/div[2]/div[1]/div/div/div[5]/ul[1]/li/a[1]"
            )
            if not profile_links:
                logger.warning("No profile links found on this page")
                break
            for link in profile_links:
                try:
                    profile_url = link.get_attribute("href")
                    driver.get(profile_url)
                    time.sleep(PAGE_LOAD_WAIT)
                    profile_data = scrape_lawyer_profile()
                    profile_data["Practice Area"] = practice_area
                    profile_data["State Area"] = state_name
                    all_profiles.append(profile_data)
                    lawyers_scraped += 1
                    driver.back()
                    time.sleep(PAGE_LOAD_WAIT)
                except Exception as e:
                    logger.error(f"Error processing profile: {str(e)}")
                    continue
            if lawyers_scraped < total_lawyers:
                next_page_xpath = (
                    f"/html/body/div[2]/div[1]/div/div/div[5]/ul[2]/li[{current_page + 1}]/a"
                )
                if safe_click(next_page_xpath):
                    current_page += 1
                    time.sleep(PAGE_LOAD_WAIT)
                else:
                    logger.warning("Couldn't find next page button")
                    break
        except Exception as e:
            logger.error(f"Error processing page {current_page}: {str(e)}")
            break
    return all_profiles


def scrape_practice_area(practice_xpath, practice_name):
    if not safe_click(practice_xpath):
        logger.warning(f"Failed to click practice area: {practice_name}")
        return
    time.sleep(PAGE_LOAD_WAIT)
    state_urls = []
    try:
        state_elements = driver.find_elements(
            By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[3]/ul/li/a"
        ) + driver.find_elements(By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[4]/ul/li/a")
        for el in state_elements:
            state_urls.append({"name": el.text.strip(), "url": el.get_attribute("href")})
    except Exception as e:
        logger.warning(f"Couldn't find state links: {str(e)}")
        return

    all_profiles = []
    for state in state_urls:
        logger.info(f"Processing state: {state['name']}")
        driver.get(state["url"])
        time.sleep(PAGE_LOAD_WAIT)
        try:
            state_profiles = scrape_state_lawyers(practice_name, state["name"])
            all_profiles.extend(state_profiles)
            if state_profiles:
                save_to_excel(state_profiles, practice_name)
        except Exception as e:
            logger.error(f"Failed processing state {state['name']}: {str(e)}")
        driver.back()
        time.sleep(PAGE_LOAD_WAIT)
    return all_profiles


def save_to_excel(data, practice_area):
    if not data:
        return
    file_path = os.path.join(OUTPUT_FOLDER, "lawyers_data.xlsx")
    columns = [
        "Name",
        "Email",
        "City",
        "State",
        "Website",
        "Update Date",
        "Practice Areas",
        "Practice Area",
        "State Area",
    ]
    sheet_name = re.sub(r"[\\/*?:\[\]]", "", practice_area[:31])
    try:
        if os.path.exists(file_path):
            with pd.ExcelWriter(
                file_path, mode="a", engine="openpyxl", if_sheet_exists="replace"
            ) as writer:
                pd.DataFrame(data, columns=columns).to_excel(
                    writer, sheet_name=sheet_name, index=False
                )
        else:
            pd.DataFrame(data, columns=columns).to_excel(
                file_path, sheet_name=sheet_name, index=False
            )
        logger.info(f"Saved {len(data)} records to sheet: {sheet_name}")
    except Exception as e:
        logger.error(f"Error saving to Excel: {str(e)}")


def main():
    try:
        driver.get(BASE_URL)
        time.sleep(PAGE_LOAD_WAIT)
        practice_areas = []
        elements = driver.find_elements(By.XPATH, "/html/body/div[2]/div[2]/div/div[15]/ul/li/a")
        for idx, element in enumerate(elements, 1):
            practice_areas.append(
                {
                    "name": element.text.strip(),
                    "xpath": f"/html/body/div[2]/div[2]/div/div[15]/ul/li[{idx}]/a",
                }
            )
        elements = driver.find_elements(By.XPATH, "/html/body/div[2]/div[2]/div/div[16]/ul/li/a")
        for idx, element in enumerate(elements, 1):
            practice_areas.append(
                {
                    "name": element.text.strip(),
                    "xpath": f"/html/body/div[2]/div[2]/div/div[16]/ul/li[{idx}]/a",
                }
            )
        for practice in practice_areas[:3]:
            logger.info(f"Starting practice area: {practice['name']}")
            scrape_practice_area(practice["xpath"], practice["name"])
    except Exception as e:
        logger.error(f"Fatal error in main(): {str(e)}")
    finally:
        driver.quit()
        logger.info("Scraping completed and driver closed")


if __name__ == "__main__":
    main()
