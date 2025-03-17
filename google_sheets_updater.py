import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

SERVICE_ACCOUNT_KEY_PATH = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
SHEET_NAME = "Bar Association Emails Task Log"  # Ensure this is correct

# Authenticate Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH, scopes=scope)
client = gspread.authorize(creds)

def append_to_google_sheet(data):
    """Append data to Google Sheets and verify the last row."""
    sheet = client.open(SHEET_NAME).sheet1
    sheet.append_row(data)
    last_row = sheet.get_all_values()[-1]  # Fetch last row for verification
    print(f"✅ Data successfully added to Google Sheets! Last Row: {last_row}")

# Example usage (Test)
if __name__ == "__main__":
    sample_data = ["Test Lawyer", "test@example.com", "123 Test St", "Test City", "12345"]
    append_to_google_sheet(sample_data)
