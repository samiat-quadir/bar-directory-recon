"""
Notification Agent - Phase 4 Optimize Prime - Alienware Device Version
Urgent lead notification system with email and SMS capabilities

Device Origin: Alienware Desktop/Workstation
Generated: July 15, 2025
"""

import logging
import smtplib
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
import json

# Optional SMS capabilities
try:
    import requests
    from twilio.rest import Client  # type: ignore
    SMS_AVAILABLE = True
    TWILIO_AVAILABLE = True
except ImportError:
    SMS_AVAILABLE = False
    TWILIO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """Configuration for notification services."""
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    from_email: str = ""
    to_emails: Optional[List[str]] = None

    # SMS settings (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    to_phone_numbers: Optional[List[str]] = None

    # Slack webhook (optional)
    slack_webhook_url: str = ""

    def __post_init__(self) -> None:
        if self.to_emails is None:
            self.to_emails = []
        if self.to_phone_numbers is None:
            self.to_phone_numbers = []


class NotificationAgent:
    """Handles urgent lead notifications via multiple channels."""

    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or self._load_config_from_env()
        self.notification_history: List[Dict[str, Any]] = []

    def _load_config_from_env(self) -> NotificationConfig:
        """Load notification configuration from environment variables."""
        return NotificationConfig(
            # Email config
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            email_username=os.getenv('EMAIL_USERNAME', ''),
            email_password=os.getenv('EMAIL_PASSWORD', ''),
            from_email=os.getenv('FROM_EMAIL', ''),
            to_emails=os.getenv('TO_EMAILS', '').split(',') if os.getenv('TO_EMAILS') else [],

            # SMS config
            twilio_account_sid=os.getenv('TWILIO_ACCOUNT_SID', ''),
            twilio_auth_token=os.getenv('TWILIO_AUTH_TOKEN', ''),
            twilio_from_number=os.getenv('TWILIO_FROM_NUMBER', ''),
            to_phone_numbers=os.getenv('TO_PHONE_NUMBERS', '').split(',') if os.getenv('TO_PHONE_NUMBERS') else [],

            # Slack config
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL', '')
        )

    def notify_urgent_leads(
        self, urgent_leads: List[Dict[str, Any]], campaign_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send notifications for urgent leads across all configured channels."""
        if not urgent_leads:
            logger.info("No urgent leads to notify")
            return {"success": True, "notifications_sent": 0, "channels": []}

        campaign_info = campaign_info or {}
        notification_results: Dict[str, Any] = {
            "email": False,
            "sms": False,
            "slack": False,
            "errors": []
        }

        # Prepare notification content
        notification_data = self._prepare_notification_content(urgent_leads, campaign_info)

        # Send email notifications
        if self.config.to_emails and self.config.email_username:
            try:
                email_success = self._send_email_notification(notification_data)
                notification_results["email"] = email_success
                if email_success:
                    logger.info(f"Email notification sent to {len(self.config.to_emails)} recipients")
            except Exception as e:
                error_msg = f"Email notification failed: {e}"
                logger.error(error_msg)
                notification_results["errors"].append(error_msg)

        # Send SMS notifications
        if self.config.to_phone_numbers and self.config.twilio_account_sid and SMS_AVAILABLE:
            try:
                sms_success = self._send_sms_notification(notification_data)
                notification_results["sms"] = sms_success
                if sms_success:
                    logger.info(f"SMS notification sent to {len(self.config.to_phone_numbers)} numbers")
            except Exception as e:
                error_msg = f"SMS notification failed: {e}"
                logger.error(error_msg)
                notification_results["errors"].append(error_msg)

        # Send Slack notifications
        if self.config.slack_webhook_url:
            try:
                slack_success = self._send_slack_notification(notification_data)
                notification_results["slack"] = slack_success
                if slack_success:
                    logger.info("Slack notification sent successfully")
            except Exception as e:
                error_msg = f"Slack notification failed: {e}"
                logger.error(error_msg)
                notification_results["errors"].append(error_msg)

        # Track notification history
        self.notification_history.append({
            "timestamp": datetime.now().isoformat(),
            "urgent_leads_count": len(urgent_leads),
            "results": notification_results,
            "campaign_info": campaign_info
        })

        # Calculate success metrics
        channels_attempted = sum(
            1 for k, v in notification_results.items()
            if k != "errors" and self._channel_configured(k)
        )
        channels_successful = sum(1 for k, v in notification_results.items() if k != "errors" and v)

        return {
            "success": channels_successful > 0,
            "notifications_sent": channels_successful,
            "channels_attempted": channels_attempted,
            "channels_successful": channels_successful,
            "urgent_leads_count": len(urgent_leads),
            "results": notification_results
        }

    def _prepare_notification_content(
        self, urgent_leads: List[Dict[str, Any]], campaign_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """Prepare notification content for all channels."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        leads_count = len(urgent_leads)

        # Get campaign details
        industry = campaign_info.get("industry", "Unknown").replace("_", " ").title()
        city = campaign_info.get("city", "Unknown")
        state = campaign_info.get("state", "")
        location = f"{city}, {state}" if state else city

        # Create lead summaries
        lead_summaries = []
        for i, lead in enumerate(urgent_leads[:5], 1):  # Show top 5 urgent leads
            urgency_reason = lead.get("urgency_reason", "High lead score")
            name = lead.get("name", "Unknown")
            company = lead.get("company", "")
            email = lead.get("email", "")
            phone = lead.get("phone", "")
            score = lead.get("lead_score", 0)

            summary = f"{i}. {name}"
            if company:
                summary += f" ({company})"
            summary += f" - Score: {score}/100"
            if email:
                summary += f" | {email}"
            if phone:
                summary += f" | {phone}"
            summary += f" | Reason: {urgency_reason}"

            lead_summaries.append(summary)

        # Email subject and content
        email_subject = f"🚨 {leads_count} Urgent Lead{'s' if leads_count != 1 else ''} - {industry} in {location}"

        email_body = f"""
🚨 URGENT LEAD ALERT 🚨

Campaign: {industry} Lead Generation
Location: {location}
Time: {timestamp}
Urgent Leads Found: {leads_count}

TOP URGENT LEADS:
{chr(10).join(lead_summaries)}

{"..." if len(urgent_leads) > 5 else ""}

These leads have been flagged as urgent based on:
- High lead scores (80+)
- Premium business indicators
- Verified contact information
- Industry-specific urgency factors

🎯 RECOMMENDED ACTIONS:
1. Contact these leads within 24 hours
2. Prioritize leads with highest scores
3. Use personalized outreach based on urgency reasons
4. Follow up within 48-72 hours if no initial response

Generated by Universal Lead Generation System - Phase 4 Optimize Prime
"""

        # SMS content (shorter)
        top_lead_name = urgent_leads[0].get('name', 'Unknown')
        top_lead_score = urgent_leads[0].get('lead_score', 0)
        sms_content = (
            f"🚨 {leads_count} urgent lead{'s' if leads_count != 1 else ''} found for {industry} "
            f"in {location}! Top lead: {top_lead_name} (Score: {top_lead_score}/100). Check email for details."
        )

        # Slack content (formatted)
        slack_content = {
            "text": f"🚨 Urgent Lead Alert - {industry}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {leads_count} Urgent Lead{'s' if leads_count != 1 else ''} Found"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Campaign:* {industry}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Location:* {location}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:* {timestamp}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Urgent Leads:* {leads_count}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Top Leads:*\\n{chr(10).join(lead_summaries[:3])}"
                    }
                }
            ]
        }

        return {
            "email_subject": email_subject,
            "email_body": email_body,
            "sms_content": sms_content,
            "slack_content": json.dumps(slack_content)
        }

    def _send_email_notification(self, notification_data: Dict[str, str]) -> bool:
        """Send email notification."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email or self.config.email_username
            msg['To'] = ', '.join(self.config.to_emails or [])
            msg['Subject'] = notification_data["email_subject"]

            # Add body
            body = MIMEText(notification_data["email_body"], 'plain')
            msg.attach(body)

            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)

            text = msg.as_string()
            server.sendmail(self.config.from_email or self.config.email_username, self.config.to_emails or [], text)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def _send_sms_notification(self, notification_data: Dict[str, str]) -> bool:
        """Send SMS notification via Twilio."""
        if not SMS_AVAILABLE:
            logger.warning("SMS notifications require 'requests' package")
            return False

        try:
            # Try to import Twilio client
            if not TWILIO_AVAILABLE:
                logger.warning("SMS notifications require 'twilio' package")
                return False

            client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)

            success_count = 0
            for phone_number in (self.config.to_phone_numbers or []):
                try:
                    message = client.messages.create(
                        body=notification_data["sms_content"],
                        from_=self.config.twilio_from_number,
                        to=phone_number.strip()
                    )
                    success_count += 1
                    logger.debug(f"SMS sent successfully. Message SID: {message.sid}")
                except Exception as e:
                    logger.error(f"Failed to send SMS to {self._sanitize_phone_number(phone_number)}: {e}")

            return success_count > 0

        except ImportError:
            logger.warning("SMS notifications require 'twilio' package")
            return False
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")
            return False

    def _send_slack_notification(self, notification_data: Dict[str, str]) -> bool:
        """Send Slack notification via webhook."""
        if not SMS_AVAILABLE:  # Using same requests availability check
            logger.warning("Slack notifications require 'requests' package")
            return False

        try:
            response = requests.post(
                self.config.slack_webhook_url,
                headers={'Content-Type': 'application/json'},
                data=notification_data["slack_content"]
            )

            if response.status_code == 200:
                return True
            else:
                logger.error(f"Slack webhook failed with status {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    def _sanitize_phone_number(self, phone_number: str) -> str:
        """Sanitize phone number to mask sensitive information."""
        if len(phone_number) > 4:
            return f"***{phone_number[-4:]}"  # Mask all but the last 4 digits
        return "***"  # Fully mask if the number is too short


    def _channel_configured(self, channel: str) -> bool:
        """Check if a notification channel is properly configured."""
        if channel == "email":
            return bool(self.config.to_emails and self.config.email_username)
        elif channel == "sms":
            return bool(self.config.to_phone_numbers and self.config.twilio_account_sid and SMS_AVAILABLE)
        elif channel == "slack":
            return bool(self.config.slack_webhook_url)
        return False

    def get_notification_summary(self) -> Dict[str, Any]:
        """Get summary of notification history and configuration."""
        total_notifications = len(self.notification_history)
        total_urgent_leads = sum(item["urgent_leads_count"] for item in self.notification_history)

        # Channel configuration status
        channels_configured = {
            "email": self._channel_configured("email"),
            "sms": self._channel_configured("sms"),
            "slack": self._channel_configured("slack")
        }

        return {
            "total_notifications_sent": total_notifications,
            "total_urgent_leads_notified": total_urgent_leads,
            "channels_configured": channels_configured,
            "recent_notifications": self.notification_history[-5:] if self.notification_history else []
        }


def notify_urgent_leads(
    urgent_leads: List[Dict[str, Any]],
    campaign_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to send urgent lead notifications.

    Args:
        urgent_leads: List of urgent leads to notify about
        campaign_info: Campaign metadata (industry, city, state, etc.)

    Returns:
        Dictionary with notification results
    """
    agent = NotificationAgent()
    return agent.notify_urgent_leads(urgent_leads, campaign_info)


def setup_notification_config(
    email_config: Optional[Dict[str, Any]] = None,
    sms_config: Optional[Dict[str, Any]] = None,
    slack_config: Optional[Dict[str, Any]] = None
) -> NotificationConfig:
    """
    Setup notification configuration programmatically.

    Args:
        email_config: Email configuration dict
        sms_config: SMS/Twilio configuration dict
        slack_config: Slack webhook configuration dict

    Returns:
        NotificationConfig object
    """
    config = NotificationConfig()

    if email_config:
        config.smtp_server = email_config.get("smtp_server", config.smtp_server)
        config.smtp_port = email_config.get("smtp_port", config.smtp_port)
        config.email_username = email_config.get("username", "")
        config.email_password = email_config.get("password", "")
        config.from_email = email_config.get("from_email", "")
        config.to_emails = email_config.get("to_emails", [])

    if sms_config:
        config.twilio_account_sid = sms_config.get("account_sid", "")
        config.twilio_auth_token = sms_config.get("auth_token", "")
        config.twilio_from_number = sms_config.get("from_number", "")
        config.to_phone_numbers = sms_config.get("to_numbers", [])

    if slack_config:
        config.slack_webhook_url = slack_config.get("webhook_url", "")

    return config


if __name__ == "__main__":
    # Test notification system
    test_urgent_leads = [
        {
            "name": "John Smith",
            "company": "Smith Pool Services",
            "email": "john@smithpools.com",
            "phone": "(555) 123-4567",
            "lead_score": 95,
            "urgency_flag": True,
            "urgency_reason": "Premium business with verified contact info"
        },
        {
            "name": "Sarah Johnson",
            "company": "Johnson Legal Group",
            "email": "sarah@johnsonlaw.com",
            "phone": "(555) 987-6543",
            "lead_score": 88,
            "urgency_flag": True,
            "urgency_reason": "High-revenue potential client"
        }
    ]

    test_campaign_info = {
        "industry": "pool_contractors",
        "city": "Miami",
        "state": "FL"
    }

    # Test with environment variables or dummy config
    try:
        result = notify_urgent_leads(test_urgent_leads, test_campaign_info)
        print(f"Notification test result: {result}")
    except Exception as e:
        print(f"Notification test failed (expected without config): {e}")

    # Test configuration setup
    agent = NotificationAgent()
    summary = agent.get_notification_summary()
    print(f"Notification agent summary: {summary}")
