import json
import logging
import os

<<<<<<< HEAD
=======
import sys

>>>>>>> 3ccf4fd (Committing all changes)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

<<<<<<< HEAD
# Import directly, without sys.path modification
from env_loader import load_environment

# Initialize environment
=======
# Ensure root project path is in sys.path
try:
    from project_path import set_root_path

    set_root_path()
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env_loader import load_environment

>>>>>>> 3ccf4fd (Committing all changes)
load_environment()

# Constants
CLIENT_SECRET_FILE = os.getenv("GMAIL_CREDENTIALS_PATH")
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
LOG_FILE = "gmail_auth.log"

logging.basicConfig(
<<<<<<< HEAD
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
=======
    filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8"
>>>>>>> 3ccf4fd (Committing all changes)
)


def authenticate_gmail():
"""TODO: Add docstring."""
    creds = None
    try:
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logging.info("🔄 Token refreshed successfully.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                logging.info("✅ New token generated successfully.")

            with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())

        print("✅ Gmail authentication successful!")

    except Exception as e:
        logging.error(f"❌ Authentication failed: {e}")
        print(f"❌ Authentication failed: {e}")


def revoke_token():
"""TODO: Add docstring."""
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            logging.info("🗑️ Token revoked and deleted successfully.")
            print("🗑️ Token revoked successfully.")
        else:
            print("⚠️ No token found to revoke.")
    except Exception as e:
        logging.error(f"❌ Failed to revoke token: {e}")
        print(f"❌ Failed to revoke token: {e}")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Authenticate Gmail (Generate/Refresh Token)")
    print("2. Revoke Token (Delete Existing Token)")

    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        authenticate_gmail()
    elif choice == "2":
        revoke_token()
    else:
        print("❌ Invalid choice. Exiting.")
