from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env")

# Gmail API token path
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")
SENDER_EMAIL = "sam.quadir@gmail.com"  # Authenticated sender email
RECIPIENT_EMAIL = "samq@damg.com"  # Primary recipient
CC_EMAILS = ["jasmin@damg.com", "sam.quadir@gmail.com"]  # CC list

def send_notification(subject, body):
    """Send an email notification via Gmail API with CC functionality."""
    try:
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH)
        service = build("gmail", "v1", credentials=creds)
        
        message = MIMEText(body)
        message["to"] = RECIPIENT_EMAIL
        message["cc"] = ", ".join(CC_EMAILS)
        message["from"] = SENDER_EMAIL
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {"raw": encoded_message}

        service.users().messages().send(userId="me", body=send_message).execute()
        print(f"✅ Notification sent: {subject}")

    except Exception as e:
        print(f"❌ Error sending notification: {e}")

# Example usage (Test)
if __name__ == "__main__":
    send_notification("Test Notification", "Your AI integration is ready to receive notifications!")
