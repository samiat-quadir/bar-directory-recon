import os
import sys
from email.message import EmailMessage
from datetime import datetime

# Load project path dynamically
from project_path import set_root_path
set_root_path()

from env_loader import load_environment
load_environment()

def build_task_subject():
    now = datetime.now().strftime("%A, %b %d @ %I:%M %p")
    return f"Review Auto Git Commit – {now}"

def build_task_body():
    return "Review the latest git auto-commit.\nPriority: high, Duration: 15min, by tomorrow."

def send_task_email():
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from base64 import urlsafe_b64encode

        creds = Credentials.from_authorized_user_file(os.getenv("GMAIL_TOKEN_PATH"))
        service = build('gmail', 'v1', credentials=creds)

        message = EmailMessage()
        message.set_content(build_task_body())
        message['To'] = "tasks@usemotion.com"
        message['From'] = os.getenv("GMAIL_USER")
        message['Subject'] = build_task_subject()

        raw_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
        send_message = service.users().messages().send(userId="me", body=raw_message).execute()

        print("Motion task email sent successfully.")
        with open("motion_email_task.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Sent task email: {message['Subject']}\n")

    except Exception as e:
        print(f"Failed to send Motion task email: {e}")

if __name__ == "__main__":
    send_task_email()
