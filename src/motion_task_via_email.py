import os
import sys
import base64
import logging
from datetime import datetime, timedelta

# === Add parent directory to path so we can import env_loader ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from env_loader import load_environment

# === Setup ===
load_environment()

# Logging
logging.basicConfig(
    filename="motion_email_task.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Load environment
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
GMAIL_USER = os.getenv("GMAIL_USER")

def create_task_email(subject_text, body_text):
    try:
        # Load Gmail credentials
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH)

        service = build("gmail", "v1", credentials=creds)

        # Create message
        message = MIMEText(body_text)
        message['to'] = "tasks@usemotion.com"
        message['from'] = GMAIL_USER
        message['subject'] = subject_text

        raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        # Send the message
        send_result = service.users().messages().send(userId="me", body=raw_message).execute()
        logging.info(f"Task email sent to Motion. ID: {send_result['id']}")
        print(" Motion task email sent successfully.")

    except Exception as e:
        logging.error(f" Failed to send Motion task email: {e}")
        print(f" Motion task email error: {e}")


# === EXAMPLE USAGE ===
if __name__ == "__main__":
    now = datetime.now()
    subject = f"Work Desktop Automation Task - {now.strftime('%b %d, %Y %I:%M %p')}"
    body = "Set up automated sync between Git and Motion. High priority. Due by tomorrow, 15min"
    
    create_task_email(subject, body)
