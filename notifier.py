import os
import pickle
import base64
import logging
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Environment Variables
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
TO_EMAILS = ["samq@damg.com", "jasmin@damg.com", "sam.quadir@gmail.com"]  # Recipients

# Configure logging
LOG_FILE = "notifier.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_credentials():
    """Load Gmail API credentials, refresh token if expired."""
    try:
        creds = None
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token_file:
                creds = pickle.load(token_file)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, "wb") as token_file:
                    pickle.dump(creds, token_file)
            else:
                raise Exception("❌ No valid credentials available. Run the authentication script.")
        return creds
    except Exception as e:
        logging.error(f"❌ Error loading credentials: {e}")
        raise

def send_email(subject, body, html=False):
    """Send an email using Gmail API."""
    try:
        creds = load_credentials()
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(body, "html" if html else "plain")
        message["to"] = ", ".join(TO_EMAILS)
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = {"raw": raw_message}
        service.users().messages().send(userId="me", body=send_message).execute()

        logging.info("✅ Email notification sent successfully.")
        print("✅ Email notification sent successfully.")
    except HttpError as error:
        logging.error(f"❌ Gmail API error: {error}")
        print(f"❌ Gmail API error: {error}")
    except Exception as e:
        logging.error(f"❌ Email notification failed: {e}")
        print(f"❌ Email notification failed: {e}")

if __name__ == "__main__":
    send_email("Test Email", "<b>✅ Gmail API notification is working successfully.</b>", html=True)
