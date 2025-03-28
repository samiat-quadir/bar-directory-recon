import os, json, time, logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==== SETUP ====
OUTPUT_DIR = "output"
LOG_FILE = f"recon_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(OUTPUT_DIR, LOG_FILE),
                    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==== CORE FUNCTIONS ====
def init_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless: options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_ajax(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)  # Allow further dynamic loads
    except Exception as e:
        logging.warning(f"AJAX wait failed: {e}")

def submit_blank_form(driver):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for b in buttons:
            if "search" in b.text.lower():
                b.click()
                logging.info("Clicked search button.")
                wait_for_ajax(driver)
                return True
        logging.warning("Search button not found.")
    except Exception as e:
        logging.error(f"Form submission failed: {e}")
    return False

def extract_emails(driver):
    emails = set()
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href^='mailto']")
        for link in links:
            href = link.get_attribute("href")
            if href: emails.add(href.replace("mailto:", "").strip())
    except Exception as e:
        logging.warning(f"Email extraction failed: {e}")
    return list(emails)

def detect_profiles(driver):
    profiles = []
    try:
        containers = driver.find_elements(By.XPATH, "//div[contains(@class,'profile') or contains(@class,'result')]")
        for el in containers:
            profiles.append(el.text[:300])
    except Exception as e:
        logging.error(f"Profile detection failed: {e}")
    return profiles

def handle_pagination(driver):
    try:
        while True:
            next_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Next') or contains(text(), 'Load More')]")
            if not next_buttons: break
            next_buttons[0].click()
            wait_for_ajax(driver)
            logging.info("Navigated to next page.")
    except Exception as e:
        logging.error(f"Pagination failed: {e}")

# ==== MAIN ====
def analyze_directory(url):
    driver = init_driver()
    result = {"url": url, "emails": [], "profiles": [], "timestamp": datetime.now().isoformat()}
    try:
        driver.get(url)
        wait_for_ajax(driver)
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "landing.png"))

        submitted = submit_blank_form(driver)
        if submitted:
            driver.save_screenshot(os.path.join(OUTPUT_DIR, "post_submit.png"))

        result["emails"] = extract_emails(driver)
        result["profiles"] = detect_profiles(driver)

        handle_pagination(driver)

    except Exception as e:
        logging.error(f"Critical failure on {url}: {e}")
    finally:
        with open(os.path.join(OUTPUT_DIR, "recon_result.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        driver.quit()
    return result

# ==== RUN ====
if __name__ == "__main__":
    target = input("Enter URL to analyze: ")
    data = analyze_directory(target)
    print(json.dumps(data, indent=2))
