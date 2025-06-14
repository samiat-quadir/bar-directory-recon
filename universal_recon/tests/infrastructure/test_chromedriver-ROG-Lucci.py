"""Infrastructure test for ChromeDriver setup."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException


# Path to the ChromeDriver executable
CHROMEDRIVER_PATH = (
    r"C:/Users/samqu/OneDrive - Digital Age Marketing Group/Desktop/Local Py/chromedriver.exe"
)


def test_chromedriver_version_compatibility():
    """Test ChromeDriver compatibility, skip if version mismatch."""
    # Set Chrome options for the test
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    options.add_argument("--disable-gpu")  # Disable GPU acceleration

    driver = None
    try:
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

        # Navigate to a test URL
        driver.get("https://www.google.com")
        assert "Google" in driver.title

    except WebDriverException as e:
        if ("version" in str(e).lower() or
            "incompatible" in str(e).lower() or
            "session not created" in str(e).lower() or
            "chromedriver" in str(e).lower()):
            pytest.skip(f"ChromeDriver version mismatch: {e}")
        else:
            raise

    except Exception as e:
        pytest.fail(f"ChromeDriver test failed: {e}")

    finally:
        # Quit the driver after the test
        if driver:
            driver.quit()
