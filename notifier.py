import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")  # Path to token.pickle
SENDER_EMAIL = "sam.quadir@gmail.com"  # Authorized email (same as used for token)
TO_EMAILS = ["samq@damg.com", "jasmin@damg.com"]
CC_EMAILS = ["sam.quadir@gmail.com"]  # Add CC emails if needed

def load_credentials():
    """Load Google OAuth2 credentials from token.pickle"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token_file:
            creds = pickle.load(token_file)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds

def send_email(subject, body):
    """Send an email notification via Gmail API"""
    creds = load_credentials()
    if not creds or not creds.valid:
        print("❌ Invalid credentials. Please re-authenticate.")
        return

    try:
        service = build("gmail", "v1", credentials=creds)

        # Create email message
        message = MIMEText(body)
        message["to"] = ", ".join(TO_EMAILS)
        message["cc"] = ", ".join(CC_EMAILS)
        message["from"] = SENDER_EMAIL
        message["subject"] = subject

        raw_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
        service.users().messages().send(userId="me", body=raw_message).execute()
        
        print("✅ Email notification sent successfully.")

    except Exception as e:
        print(f"❌ Email notification failed: {e}")

if __name__ == "__main__":
    send_email("Test Email", "✅ Gmail API notification is working successfully.")
