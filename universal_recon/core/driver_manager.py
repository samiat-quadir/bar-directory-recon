from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class DriverManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        headless = self.config.get("general.headless", True)
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        self.logger.log("WebDriver initialized.")

    def fetch_page(self, url, retries=3):
        for attempt in range(1, retries + 1):
            try:
                self.logger.log(f"Fetching page: {url} (Attempt {attempt})")
                self.driver.get(url)
                return True
            except Exception as e:
                self.logger.log(f"Fetch error: {str(e)}", level="ERROR")
        return False

    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.log("WebDriver closed.")
            except Exception as e:
                self.logger.log(f"Error closing WebDriver: {e}", level="WARN")
            self.driver = None
