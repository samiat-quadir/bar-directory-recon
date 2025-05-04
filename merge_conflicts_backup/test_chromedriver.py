from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Path to the ChromeDriver executable
CHROMEDRIVER_PATH = r"C:/Users/samqu/OneDrive - Digital Age Marketing Group/Desktop/Local Py/chromedriver.exe"

# Set Chrome options for the test
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no browser UI)
options.add_argument("--disable-gpu")  # Disable GPU acceleration

try:
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    # Navigate to a test URL
    driver.get("https://www.google.com")
    print("Test Passed: ChromeDriver is working.")

except Exception as e:
    # Print any errors that occur during execution
    print(f"Test Failed: {e}")

finally:
    # Quit the driver after the test
    driver.quit()
