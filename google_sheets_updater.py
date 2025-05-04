import logging
import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Environment Variables
SERVICE_ACCOUNT_KEY_PATH = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
SHEET_ID = os.getenv("SHEET_ID")  # Using Sheet ID instead of Sheet Name

# Configure logging
LOG_FILE = "google_sheets_updater.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Authenticate Google Sheets API
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    logging.info("✅ Google Sheets authentication successful.")
except Exception as e:
    logging.error(f"❌ Failed to authenticate Google Sheets: {e}")
    raise


def append_to_google_sheet(data):
    """Append data to Google Sheets with error handling and logging."""
    try:
        sheet = client.open_by_key(SHEET_ID).sheet1  # Open by Sheet ID
        sheet.append_row(data)
        logging.info(f"✅ Data successfully added: {data}")
        print("✅ Data successfully added to Google Sheets!")
    except gspread.exceptions.APIError as e:
        logging.error(f"❌ Google Sheets API Error: {e}")
        print(f"❌ Google Sheets API Error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected Error: {e}")
        print(f"❌ Unexpected Error: {e}")


# Example Usage (Test)
if __name__ == "__main__":
    sample_data = [
        "Test Lawyer",
        "test@example.com",
        "123 Test St",
        "Test City",
        "12345",
    ]
    append_to_google_sheet(sample_data)
