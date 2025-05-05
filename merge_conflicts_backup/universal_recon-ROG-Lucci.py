"""
Universal Recon Tool (v2 Beta with Log Manager)
Recursively scans any Bar directory site to collect key scraping metadata.
Outputs JSON recon report + screenshots + logs.
"""

import json
import logging
import os

<<<<<<< HEAD
=======
import time

>>>>>>> 3ccf4fd (Committing all changes)
from datetime import datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver

<<<<<<< HEAD
from selenium.common.exceptions import WebDriverException

=======
from selenium.common.exceptions import TimeoutException, WebDriverException

>>>>>>> 3ccf4fd (Committing all changes)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Load .env file
load_dotenv(dotenv_path="C:/Users/samqu/OneDrive - Digital Age Marketing Group/Desktop/Local Py/.env")

# Constants
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
TIMEOUT = 15
MAX_IFRAME_DEPTH = 5

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "..", "screenshots")
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")

# Ensure directories exist
for directory in [OUTPUT_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Logging configuration
log_filename = os.path.join(LOGS_DIR, f"recon_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(
    filename=log_filename,
    filemode="w",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


# Utility functions
def timestamp():
"""TODO: Add docstring."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_json(data, name):
"""TODO: Add docstring."""
    with open(os.path.join(OUTPUT_DIR, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_screenshot(driver, name):
"""TODO: Add docstring."""
    driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"{name}.png"))


def recon_page(driver, depth=0, path="root"):
"""TODO: Add docstring."""
    if depth > MAX_IFRAME_DEPTH:
        return []
    logging.info(f"Recon at depth {depth}, path: {path}")
<<<<<<< HEAD
    frame_data = {
        "path": path,
        "forms": [],
        "buttons": [],
        "pagination": [],
        "profile_containers": [],
    }
=======
    frame_data = {"path": path, "forms": [], "buttons": [], "pagination": [], "profile_containers": []}
>>>>>>> 3ccf4fd (Committing all changes)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    for form in driver.find_elements(By.TAG_NAME, "form"):
        inputs = []
        for field in form.find_elements(By.XPATH, ".//input | .//textarea | .//select"):
            inputs.append(
                {
                    "name": field.get_attribute("name"),
                    "type": field.get_attribute("type"),
                    "placeholder": field.get_attribute("placeholder"),
                }
            )
        frame_data["forms"].append({"form_id": form.get_attribute("id"), "inputs": inputs})

    for button in driver.find_elements(By.XPATH, "//button | //input[@type='submit']"):
        frame_data["buttons"].append(
<<<<<<< HEAD
            {
                "text": button.text,
                "classes": button.get_attribute("class"),
                "id": button.get_attribute("id"),
            }
=======
            {"text": button.text, "classes": button.get_attribute("class"), "id": button.get_attribute("id")}
>>>>>>> 3ccf4fd (Committing all changes)
        )

    pagination_candidates = driver.find_elements(
        By.XPATH,
        "//a[contains(text(), 'Next')] | //button[contains(text(), 'Next')] | //a[contains(text(), 'Load More')]",
    )
    for btn in pagination_candidates:
        frame_data["pagination"].append({"text": btn.text, "outerHTML": btn.get_attribute("outerHTML")})

    for div in soup.find_all("div", class_=lambda x: x and "profile" in x.lower()):
        frame_data["profile_containers"].append(div.get("class"))

    save_screenshot(driver, f"{path}_depth_{depth}_{timestamp()}")

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for idx, iframe in enumerate(iframes):
        iframe_id = iframe.get_attribute("id") or f"iframe-{idx}"
        try:
            driver.switch_to.frame(iframe)
            frame_data.setdefault("iframes", []).append(recon_page(driver, depth + 1, f"{path}/{iframe_id}"))
            driver.switch_to.parent_frame()
        except WebDriverException as e:
            logging.warning(f"Failed to switch to iframe {iframe_id}: {e}")

    return frame_data


def universal_recon(target_url):
"""TODO: Add docstring."""
    report = {"url": target_url, "recon": []}
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(target_url)
        WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        save_screenshot(driver, f"landing_{timestamp()}")

        report["recon"] = recon_page(driver)
        save_json(report, f"recon_{timestamp()}")
        logging.info("Recon completed successfully.")

    except Exception as e:
        logging.error(f"Error during recon: {e}")
        save_screenshot(driver, f"error_{timestamp()}")
    finally:
        driver.quit()


if __name__ == "__main__":
    target = input("Enter the URL to analyze: ")
    universal_recon(target)
