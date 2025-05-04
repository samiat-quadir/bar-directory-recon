import json
import logging
import os
<<<<<<< HEAD
=======
import time
>>>>>>> 3ccf4fd (Committing all changes)

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Load environment variables
load_dotenv()
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
OUTPUT_DIR = "output/"
LOGS_DIR = "logs/"
GOOGLE_DRIVE_UPLOAD = os.getenv("GOOGLE_DRIVE_UPLOAD", "false").lower() == "true"

# Ensure directories exist
for directory in [OUTPUT_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "recon.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def init_driver():
    """Initialize the WebDriver with proper configurations."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def save_json(data, name):
    """Save extracted data as JSON."""
    with open(os.path.join(OUTPUT_DIR, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def extract_lawyers(driver, url):
    """Extract lawyer profiles from a given directory."""
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    profiles = []
    profile_elements = driver.find_elements(By.CLASS_NAME, "profile-card")
    for profile in profile_elements:
        name = profile.find_element(By.CLASS_NAME, "name").text.strip()
        email = (
            profile.find_element(By.XPATH, ".//a[contains(@href, 'mailto')]")
            .get_attribute("href")
            .replace("mailto:", "")
        )
        profiles.append({"name": name, "email": email})

    return profiles


def main():
"""TODO: Add docstring."""
    url = input("Enter the URL to analyze: ")
    driver = init_driver()

    try:
        logging.info(f"Starting recon on {url}")
        extracted_data = extract_lawyers(driver, url)
        save_json(extracted_data, "recon_results")
        logging.info("Data extraction completed successfully.")
    except Exception as e:
        logging.error(f"Error during extraction: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
