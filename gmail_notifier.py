import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")  # Ensure this path is correct
SENDER_EMAIL = "sam.quadir@gmail.com"  # Authenticated sender
RECIPIENT_EMAIL = "samq@damg.com"  # Primary recipient
CC_EMAILS = ["jasmin@damg.com", "sam.quadir@gmail.com"]  # CC list

def load_gmail_credentials():
    """Load Gmail credentials from the JSON token file."""
    if not os.path.exists(GMAIL_TOKEN_PATH):
        raise FileNotFoundError(f"⚠️ Token file not found: {GMAIL_TOKEN_PATH}")

    with open(GMAIL_TOKEN_PATH, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(json.loads(creds_data))

    if not creds or not creds.valid:
        raise ValueError("⚠️ Invalid credentials. Re-run the authentication script.")

    return creds

def send_email_notification(subject, body, recipient=RECIPIENT_EMAIL, cc_list=CC_EMAILS):
    """Send an email with dynamic subject & body, including CC recipients."""
    creds = load_gmail_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = recipient
    message["from"] = SENDER_EMAIL
    message["subject"] = subject
    message["cc"] = ", ".join(cc_list)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    send_request = {"raw": encoded_message}

    try:
        service.users().messages().send(userId="me", body=send_request).execute()
        print(f"✅ Email sent successfully to {recipient} with CC: {', '.join(cc_list)}")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

# Test
if __name__ == "__main__":
    send_email_notification("AI System Alert", "This is a dynamically generated test notification.")
