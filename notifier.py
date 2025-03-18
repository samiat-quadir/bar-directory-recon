import os
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load environment variables
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS").split(",")

# Configure logging
LOG_FILE = "notifier_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

def authenticate_gmail():
    """Authenticate Gmail API and return credentials."""
    creds = None
    if os.path.exists(GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("🔴 Authentication Failed! Please reauthorize Gmail API.")
    return creds

def send_email_notification(commit_message):
    """Send an email notification with the latest commit details."""
    try:
        creds = authenticate_gmail()
        service = build("gmail", "v1", credentials=creds)

        # Email content
        sender_email = "your_email@gmail.com"  # Update this to your email
        subject = "🚀 GitHub Auto-Commit Notification"
        body = f"""
        <h2>✅ Auto-Commit Successful!</h2>
        <p><strong>Commit Message:</strong> {commit_message}</p>
        <p><strong>Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Check your GitHub repository for changes.</p>
        """

        for recipient in EMAIL_RECIPIENTS:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient
            message["Subject"] = subject
            message.attach(MIMEText(body, "html"))

            # Send email
            send_message = {"raw": message.as_string().encode("utf-8")}
            service.users().messages().send(userId="me", body=send_message).execute()

            logging.info(f"📧 Notification sent to {recipient}")

    except Exception as e:
        logging.error(f"❌ Email notification failed: {e}")

# Watch for new commits every 15 minutes
while True:
    latest_commit = os.popen("git log -1 --pretty=%B").read().strip()
    send_email_notification(latest_commit)
    time.sleep(900)  # 15-minute interval
