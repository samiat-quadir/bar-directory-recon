import os
import re
from datetime import datetime
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from env_loader import load_environment

# === Load Environment ===
load_environment()

LOG_PATH = "automation_run.log"
EMAIL_USER = os.getenv("GMAIL_USER")
TO_EMAILS = os.getenv("TO_EMAILS").split(",")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")

SUMMARY_SUBJECT = f"Daily Automation Summary – {datetime.now().strftime('%Y-%m-%d')}"

def extract_summary(log_path):
    summary_lines = []
    if not os.path.exists(log_path):
        return ["[Warning] automation_run.log not found."]
    
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if "Running:" in line or "Loaded environment" in line:
            summary_lines.append(line.strip())
        elif "ERROR" in line or "FAILED" in line:
            summary_lines.append("⚠️ " + line.strip())

    if not summary_lines:
        summary_lines.append("[No summary data extracted.]")

    return summary_lines

def send_email_summary(body_lines):
    creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH)
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()
    message.set_content("\n".join(body_lines))
    message["To"] = ", ".join(TO_EMAILS)
    message["From"] = EMAIL_USER
    message["Subject"] = SUMMARY_SUBJECT

    from base64 import urlsafe_b64encode
    raw = {"raw": urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
    send = service.users().messages().send(userId="me", body=raw).execute()
    print("✅ Daily summary email sent.")

if __name__ == "__main__":
    summary = extract_summary(LOG_PATH)
    send_email_summary(summary)
