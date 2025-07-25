"""
Notification Manager for Universal Project Runner
==============================================

Handles sending notifications via Discord webhooks and email.
Supports both success and error notifications with rich formatting.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, cast
import requests

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages notifications via Discord and Email."""

    config: Dict[str, Any]
    discord_webhook: Optional[str]
    email_config: Dict[str, Any]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.discord_webhook = config.get("discord_webhook")
        self.email_config = config.get("email", {})

    def send_success_notification(self, title: str, message: str = "") -> None:
        """Send a success notification."""
        self._send_notification(title=title, message=message, notification_type="success", color=0x00FF00)  # Green

    def send_error_notification(self, title: str, error_details: str = "") -> None:
        """Send an error notification."""
        self._send_notification(title=title, message=error_details, notification_type="error", color=0xFF0000)  # Red

    def send_warning_notification(self, title: str, message: str = "") -> None:
        """Send a warning notification."""
        self._send_notification(title=title, message=message, notification_type="warning", color=0xFFAA00)  # Orange

    def send_info_notification(self, title: str, message: str = "") -> None:
        """Send an info notification."""
        self._send_notification(title=title, message=message, notification_type="info", color=0x0099FF)  # Blue

    def _send_notification(self, title: str, message: str, notification_type: str, color: int) -> None:
        """Send notification via all configured channels."""
        try:
            # Send to Discord if configured
            if self.discord_webhook:
                self._send_discord_notification(title, message, notification_type, color)

            # Send email if configured
            if self.email_config.get("enabled"):
                self._send_email_notification(title, message, notification_type)

            logger.info(f"Sent {notification_type} notification: {title}")

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    def _send_discord_notification(self, title: str, message: str, notification_type: str, color: int) -> None:
        """Send notification to Discord webhook."""
        try:
            # Create embed
            embed = {
                "title": f"{self._get_emoji(notification_type)} {title}",
                "description": message,
                "color": color,
                "timestamp": self._get_timestamp(),
                "footer": {
                    "text": "Bar Directory Recon - Universal Runner",
                    "icon_url": "https://example.com/icon.png",  # Replace with actual icon
                },
                "fields": [
                    {"name": "Status", "value": notification_type.title(), "inline": True},
                    {"name": "Source", "value": "Universal Runner", "inline": True},
                ],
            }
            # Add additional context based on notification type
            if notification_type == "error":
                # fields is a list, so .append is valid
                fields = cast(list, embed["fields"])
                fields.append(
                    {
                        "name": "Error Details",
                        "value": f"```{message[:1000]}```" if message else "No details available",
                        "inline": False,
                    }
                )
            payload = {"embeds": [embed], "username": "Universal Runner Bot"}
            if not self.discord_webhook:
                logger.warning("Discord webhook URL is not set. Skipping Discord notification.")
                return
            response = requests.post(str(self.discord_webhook), json=payload, timeout=10)
            if response.status_code == 204:
                logger.debug("Discord notification sent successfully")
            else:
                logger.warning(f"Discord webhook returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")

    def _send_email_notification(self, title: str, message: str, notification_type: str) -> None:
        """Send notification via email."""
        try:
            smtp_server = self.email_config.get("smtp_server")
            smtp_port = self.email_config.get("smtp_port", 587)
            username = self.email_config.get("username")
            password = self.email_config.get("password")
            recipients = self.email_config.get("recipients", [])
            # Type checks for mypy/static analysis
            valid_email = (
                isinstance(smtp_server, str)
                and isinstance(username, str)
                and isinstance(password, str)
                and isinstance(recipients, list)
                and recipients
            )
            if not valid_email:
                logger.warning("Email configuration incomplete, skipping email notification")
                return
            # Cast to str for type checker
            smtp_server_str = str(smtp_server)
            username_str = str(username)
            password_str = str(password)
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{notification_type.upper()}] {title}"
            msg["From"] = username_str
            msg["To"] = ", ".join(recipients)
            # Create HTML content
            html_content = self._create_email_html(title, message, notification_type)
            html_part = MIMEText(html_content, "html")
            # Create plain text content
            text_content = f"{title}\n\n{message}"
            text_part = MIMEText(text_content, "plain")
            msg.attach(text_part)
            msg.attach(html_part)
            # Send email
            with smtplib.SMTP(smtp_server_str, smtp_port) as server:
                server.starttls()
                server.login(username_str, password_str)
                server.send_message(msg)
            logger.debug("Email notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def _create_email_html(self, title: str, message: str, notification_type: str) -> str:
        """Create HTML content for email notifications."""
        color_map = {"success": "#28a745", "error": "#dc3545", "warning": "#ffc107", "info": "#17a2b8"}

        color = color_map.get(notification_type, "#6c757d")
        emoji = self._get_emoji(notification_type)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
                .message {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 15px 0;
                    white-space: pre-wrap;
                    font-family: monospace;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{emoji} {title}</h1>
                </div>
                <div class="content">
                    <p><strong>Status:</strong> {notification_type.title()}</p>
                    <p><strong>Source:</strong> Universal Runner</p>
                    <p><strong>Timestamp:</strong> {self._get_timestamp()}</p>

                    {f'<div class="message">{message}</div>' if message else ''}
                </div>
                <div class="footer">
                    Bar Directory Recon - Universal Runner Automation System
                </div>
            </div>
        </body>
        </html>
        """

    def _get_emoji(self, notification_type: str) -> str:
        """Get emoji for notification type."""
        emoji_map = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        return emoji_map.get(notification_type, "📢")

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    def test_notifications(self) -> None:
        """Test all notification channels."""
        logger.info("Testing notification channels...")
        self.send_info_notification("Test Notification", "This is a test message to verify notification functionality.")
        logger.info("Test notifications sent")

    def send_daily_summary(self, stats: Dict[str, Any]) -> None:
        """Send daily summary notification."""
        title = "Daily Pipeline Summary"
        message = f"""
        Pipeline Execution Summary:

        • Total runs: {stats.get('total_runs', 0)}
        • Successful: {stats.get('successful_runs', 0)}
        • Failed: {stats.get('failed_runs', 0)}
        • Sites processed: {stats.get('sites_processed', 0)}
        • Files processed: {stats.get('files_processed', 0)}

        Success rate: {stats.get('success_rate', 0):.1f}%
        """
        if stats.get("failed_runs", 0) > 0:
            self.send_warning_notification(title, message)
        else:
            self.send_success_notification(title, message)
