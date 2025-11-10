import os
import pickle
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from base64 import urlsafe_b64encode
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
TO_EMAILS = ["samq@damg.com", "sam.quadir@gmail.com"]
SENDER_EMAIL = "sam.quadir@gmail.com"  # Must match the token sender
LOG_FILE = "email_notifier.log"

# Logging Setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_credentials():
    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, "wb") as token_file:
                    pickle.dump(creds, token_file)
            return creds
        else:
            raise FileNotFoundError("Token file not found.")
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        return None

def send_email(subject, body_html):
    creds = load_credentials()
    if not creds:
        logging.error("❌ No valid credentials found. Email not sent.")
        return

    try:
        service = build("gmail", "v1", credentials=creds)

        # Build MIME Message
        message = MIMEMultipart("alternative")
        message["To"] = ", ".join(TO_EMAILS)
        message["From"] = SENDER_EMAIL
        message["Subject"] = subject

        mime_html = MIMEText(body_html, "html")
        message.attach(mime_html)

        raw = urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {"raw": raw}

        service.users().messages().send(userId="me", body=message_body).execute()
        logging.info("✅ HTML Email sent successfully.")
        print(" HTML Email sent successfully.")

    except HttpError as http_err:
        logging.error(f"📛 Gmail API error: {http_err}")
        print(f" Gmail API error: {http_err}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        print(f" Unexpected error: {e}")

if __name__ == "__main__":
    html_content = """
    <h2>✅ Gmail API HTML Notification</h2>
    <p>This is a <strong>formatted</strong> HTML email sent from the Gmail API.</p>
    <p>Auto-commit task is running as scheduled.</p>
    """
    send_email("🚀 Test HTML Notification from ASUS", html_content)
