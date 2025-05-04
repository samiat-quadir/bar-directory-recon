import os
import sys
from base64 import urlsafe_b64encode
from datetime import datetime
from email.message import EmailMessage

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ROOT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from env_loader import load_environment
from project_path import set_root_path

set_root_path()
load_environment()

EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_TO = "tasks@usemotion.com"


def build_task_subject():
    return f"Review Git Commit – {datetime.now().strftime('%b %d @ %I:%M %p')}"


def build_task_body():
    return """Review the latest auto-commit.\nPriority: high, Duration: 15min, by tomorrow."""


def send_task_email():
    try:
        creds = Credentials.from_authorized_user_file(os.getenv("GMAIL_TOKEN_PATH"))
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message.set_content(build_task_body())
        message["To"] = EMAIL_TO
        message["From"] = EMAIL_USER
        message["Subject"] = build_task_subject()

        raw_message = {"raw": urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
        service.users().messages().send(userId="me", body=raw_message).execute()

        print("Motion task email sent successfully.")
    except Exception as e:
        print(f"Failed to send Motion task email: {e}")


if __name__ == "__main__":
    send_task_email()
