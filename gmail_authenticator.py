import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")  # Path to token.pickle
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def authenticate_gmail():
    """Authenticate with Gmail API and generate a new token.pickle"""
    creds = None

    # Load existing credentials if available
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, "rb") as token_file:
                creds = pickle.load(token_file)
        except Exception:
            print("⚠️ Existing token is invalid. Regenerating a new one.")
            creds = None

    # If credentials are invalid or missing, request new authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GMAIL_CREDENTIALS_PATH"), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the new credentials in Pickle format
        with open(TOKEN_PATH, "wb") as token_file:
            pickle.dump(creds, token_file)
        print(f"✅ New token saved at {TOKEN_PATH}")

if __name__ == "__main__":
    authenticate_gmail()
