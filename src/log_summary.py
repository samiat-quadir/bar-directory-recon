import os
import logging
from datetime import datetime
from env_loader import load_environment
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.message import EmailMessage
from base64 import urlsafe_b64encode

# === SETUP ===
load_environment()
LOGS_DIR = os.path.join(os.getcwd(), 'logs')
SUMMARY_FILE = os.path.join(LOGS_DIR, 'log_summary.txt')
EMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
TO_EMAILS = os.getenv("TO_EMAILS").split(",")

def scan_logs():
    summary_lines = []
    for fname in os.listdir(LOGS_DIR):
        if fname.endswith(".log"):
            path = os.path.join(LOGS_DIR, fname)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "ERROR" in line or "WARNING" in line:
                        summary_lines.append(f"{fname}: {line.strip()}")
    return summary_lines

def send_summary(summary_lines):
    if not summary_lines:
        print("✅ No errors/warnings found.")
        return

    creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH)
    service = build('gmail', 'v1', credentials=creds)

    body = "\n".join(summary_lines)
    subject = f"Log Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    message = EmailMessage()
    message.set_content(body)
    message['To'] = ", ".join(TO_EMAILS)
    message['From'] = EMAIL_USER
    message['Subject'] = subject

    raw_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
    service.users().messages().send(userId="me", body=raw_message).execute()
    print("📬 Log summary email sent.")

if __name__ == "__main__":
    summary = scan_logs()
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(summary) if summary else "No issues detected.\n")
    send_summary(summary)
