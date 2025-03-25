# work_notifier.py (Work Desktop)
import os
import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.work')

# Logging configuration
logging.basicConfig(
    filename='email_notifier.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        os.getenv('GMAIL_TOKEN_PATH'), SCOPES)
    return build('gmail', 'v1', credentials=creds)

def send_html_notification(subject, html_content):
    service = get_gmail_service()

    message = MIMEMultipart('alternative')
    message['From'] = os.getenv('GMAIL_USER')
    message['To'] = os.getenv('TO_EMAILS')
    message['Subject'] = subject

    message.attach(MIMEText(html_content, 'html'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        message = service.users().messages().send(
            userId='me', body={'raw': raw_message}).execute()
        logging.info(f'✅ Notification email sent successfully: {message["id"]}')
    except Exception as e:
        logging.error(f'❌ Failed to send email: {e}')

if __name__ == "__main__":
    # Test notification
    send_html_notification("🚀 Test Email from Work Desktop",
                           "<h1>Notification Setup Successfully!</h1>")