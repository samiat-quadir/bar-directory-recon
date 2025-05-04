import os
import sys
from datetime import datetime
from email.mime.text import MIMEText

# === Patch path ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env_loader import load_environment

# === Load env ===
load_environment()

LOG_FILE = "automation_run.log"
EMAIL_USER = os.getenv("GMAIL_USER")
TO_EMAILS = os.getenv("TO_EMAILS", "").split(",")


def extract_summary():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start = None
    for i in range(len(lines) - 1, -1, -1):
        if "=== DAILY AUTOMATION START ===" in lines[i]:
            start = i
            break

    return "".join(lines[start:]) if start else "Log summary not found."


def send_email_summary():
    try:
        from base64 import urlsafe_b64encode

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(os.getenv("GMAIL_TOKEN_PATH"))
        service = build("gmail", "v1", credentials=creds)

        body = extract_summary()
        message = MIMEText(body)
        message["To"] = TO_EMAILS[0]
        message["From"] = EMAIL_USER
        message["Subject"] = f" Daily Automation Summary — {datetime.now().strftime('%b %d %Y')}"

        raw_message = {"raw": urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
        service.users().messages().send(userId="me", body=raw_message).execute()
        print(" Summary email sent.")
    except Exception as e:
        print(f" Failed to send summary email: {e}")


if __name__ == "__main__":
    send_email_summary()
