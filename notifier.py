import os
import pickle
import base64
import logging
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from env_loader import load_environment

# Load environment from correct file
load_environment()

# Setup logging
LOG_PATH = os.getenv("LOG_EMAIL_NOTIFIER", "email_notifier.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, encoding='utf-8', format="%(asctime)s - %(levelname)s - %(message)s")

# Environment variables
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
TO_EMAILS = os.getenv("TO_EMAILS", "").split(",")

def load_credentials():
    """Load and refresh Gmail API credentials."""
    try:
        if not GMAIL_TOKEN_PATH or not os.path.exists(GMAIL_TOKEN_PATH):
            raise FileNotFoundError("❌ GMAIL_TOKEN_PATH is not set or file doesn't exist.")

        with open(GMAIL_TOKEN_PATH, "rb") as token_file:
            creds = pickle.load(token_file)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(GMAIL_TOKEN_PATH, "wb") as token_file:
                pickle.dump(creds, token_file)

        return creds
    except Exception as e:
        logging.error(f"❌ Failed to load Gmail credentials: {e}")
        raise

def send_email_notification(subject, body):
    """Send an HTML email via Gmail API."""
    try:
        creds = load_credentials()
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(body, "html")
        message["to"] = ", ".join(TO_EMAILS)
        message["from"] = SENDER_EMAIL
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        send_message = {"raw": raw_message}

        service.users().messages().send(userId="me", body=send_message).execute()

        logging.info("✅ Email notification sent successfully.")
        print("✅ Email notification sent successfully.")
    except Exception as e:
        logging.error(f"❌ General email error: {e}")
        print(f"❌ General email error: {e}")

if __name__ == "__main__":
    print("✅ Loaded environment from .env.asus")
    print(f"📄 GMAIL_TOKEN_PATH = {GMAIL_TOKEN_PATH}")
    send_email_notification("ASUS Notification Test", "<b>This is a test email from ASUS script</b>")
