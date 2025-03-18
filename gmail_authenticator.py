import os
import pickle
import logging
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Environment Variables
CLIENT_SECRET_FILE = os.getenv("GMAIL_CREDENTIALS_PATH")
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Configure logging
LOG_FILE = "gmail_auth.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def authenticate_gmail():
    """Handles Gmail API authentication and token generation."""
    creds = None
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token_file:
                creds = pickle.load(token_file)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, "wb") as token_file:
                    pickle.dump(creds, token_file)
                logging.info("✅ Token refreshed successfully.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_PATH, "wb") as token_file:
                    pickle.dump(creds, token_file)
                logging.info("✅ New token saved successfully.")

        print("✅ Gmail authentication successful!")
    except Exception as e:
        logging.error(f"❌ Authentication failed: {e}")
        print(f"❌ Authentication failed: {e}")

def revoke_token():
    """Manually revokes the existing token."""
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            logging.info("🗑️ Token revoked and deleted successfully.")
            print("🗑️ Token revoked and deleted successfully. Please re-run authentication.")
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
11