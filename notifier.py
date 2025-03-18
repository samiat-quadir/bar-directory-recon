import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

GMAIL_USER = os.getenv("GMAIL_CREDENTIALS_PATH")
GMAIL_PASS = os.getenv("GMAIL_TOKEN_PATH")
TO_EMAILS = ["samq@damg.com", "jasmin@damg.com", "sam.quadir@gmail.com"]  # Add recipients

def send_email_notification(subject, body):
    """Send an email notification."""
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(TO_EMAILS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, TO_EMAILS, msg.as_string())
        print("✅ Email notification sent successfully.")
    except Exception as e:
        print(f"❌ Email notification failed: {e}")

if __name__ == "__main__":
    send_email_notification("Test Email", "Git commit automation notification test.")
