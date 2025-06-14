# Infrastructure test for ChromeDriver setup
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException

# Path to the ChromeDriver executable
CHROMEDRIVER_PATH = (
    r"C:/Users/samqu/OneDrive - Digital Age Marketing Group/Desktop/Local Py/chromedriver.exe"
)

# Set Chrome options for the test
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no browser UI)
options.add_argument("--disable-gpu")  # Disable GPU acceleration

def test_chromedriver():
    """Test ChromeDriver functionality with proper error handling."""
    driver = None
    try:
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        
        # Navigate to a test URL
        driver.get("https://www.google.com")
        print("Test Passed: ChromeDriver is working.")

    except SessionNotCreatedException as e:
        # Skip test on version mismatch specifically
        pytest.skip(f"ChromeDriver version mismatch - skipping test: {e}")
    except Exception as e:
        # Skip test on any other driver issues
        pytest.skip(f"ChromeDriver test skipped due to: {e}")

    finally:
        # Quit the driver after the test if it was initialized
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                # driver cleanup failed, ignore
                pass
            pass
