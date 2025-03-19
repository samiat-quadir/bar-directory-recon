import os
import pickle
import logging
from googleapiclient.discovery import build
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Environment Variables
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_RECIPIENTS = ["samq@damg.com", "jasmin@damg.com", "sam.quadir@gmail.com"]

# Configure logging
LOG_FILE = "gmail_notifier.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_credentials():
    """Loads Gmail API credentials from token file."""
    creds = None
    try:
        if os.path.exists(GMAIL_TOKEN_PATH):
            with open(GMAIL_TOKEN_PATH, "rb") as token_file:
                creds = pickle.load(token_file)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(GMAIL_TOKEN_PATH, "wb") as token_file:
                    pickle.dump(creds, token_file)
        return creds
    except Exception as e:
        logging.error(f"❌ Failed to load Gmail credentials: {e}")
        return None

def send_email(subject, body):
    """Sends an email using the Gmail API."""
    creds = load_credentials()
    if not creds:
        logging.error("❌ Unable to authenticate Gmail API.")
        return

    try:
        service = build("gmail", "v1", credentials=creds)
        message = {
            "raw": base64.urlsafe_b64encode(
                f"From: {EMAIL_SENDER}\nTo: {', '.join(EMAIL_RECIPIENTS)}\nSubject: {subject}\n\n{body}".encode("utf-8")
            ).decode("utf-8")
        }
        service.users().messages().send(userId="me", body=message).execute()
        logging.info(f"✅ Email sent: {subject}")
    except Exception as e:
        logging.error(f"❌ Email notification failed: {e}")

if __name__ == "__main__":
    # Test email for errors
    send_email("Test Email", "✅ Gmail API notification is working successfully.")
