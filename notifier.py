import base64
import json
import logging
import os
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from env_loader import load_environment

# Load environment from correct file
load_environment()

# Setup logging
LOG_PATH = os.getenv("LOG_EMAIL_NOTIFIER", "email_notifier.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Environment variables
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
TO_EMAILS = os.getenv("TO_EMAILS", "").split(",")


def load_gmail_credentials():
    creds = None
    token_path = os.getenv("GMAIL_TOKEN_PATH")

    if token_path and os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/gmail.send"])
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            logging.error(f"❌ Token loading or refreshing error: {e}")
            print(f"❌ Token loading or refreshing error: {e}")
    else:
        logging.error("❌ Token file path is incorrect or file doesn't exist.")
        print("❌ Token file path is incorrect or file doesn't exist.")

    return creds


def send_html_notification(subject, body):
    """Send an HTML email via Gmail API."""
    try:
        creds = load_gmail_credentials()
        if not creds:
            raise ValueError("Gmail credentials could not be loaded.")

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
    print("✅ Loaded environment from .env.work")
    print(f"📄 GMAIL_TOKEN_PATH = {GMAIL_TOKEN_PATH}")
    send_html_notification("Work Notification Test", "<b>This is a test email from Work Desktop script</b>")
