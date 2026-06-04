"""
Tests for notification_agent.py - Notification configuration and message handling.

Targets:
- NotificationConfig initialization
- NotificationAgent message preparation
- Color mapping and formatting
- Test notification methods (without actual sending)

All tests run without network calls or credentials.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestNotificationConfig:
    """Tests for NotificationConfig class."""

    def test_config_disabled_by_default(self):
        """NotificationConfig should be disabled by default."""
        from src.notification_agent import NotificationConfig

        config = NotificationConfig({})

        assert config.enabled is False
        assert config.email_enabled is False
        assert config.sms_enabled is False
        assert config.slack_enabled is False

    def test_config_enabled_when_set(self):
        """NotificationConfig should enable when config specifies."""
        from src.notification_agent import NotificationConfig

        config = NotificationConfig({
            "enabled": True,
            "email": {"enabled": True},
            "sms": {"enabled": False},
            "slack": {"enabled": True},
        })

        assert config.enabled is True
        assert config.email_enabled is True
        assert config.sms_enabled is False
        assert config.slack_enabled is True

    def test_config_stores_sub_configs(self):
        """NotificationConfig should store sub-configurations."""
        from src.notification_agent import NotificationConfig

        email_config = {"enabled": True, "smtp_server": "smtp.test.com"}
        sms_config = {"enabled": False, "from_number": "+1234567890"}

        config = NotificationConfig({
            "email": email_config,
            "sms": sms_config,
        })

        assert config.email_config["smtp_server"] == "smtp.test.com"
        assert config.sms_config["from_number"] == "+1234567890"


class TestNotificationAgent:
    """Tests for NotificationAgent class."""

    def test_agent_init_with_no_config(self):
        """NotificationAgent should initialize with no config."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent()

        assert agent.config.enabled is False

    def test_agent_init_with_config(self):
        """NotificationAgent should initialize with config."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        assert agent.config.enabled is True

    def test_send_notification_disabled(self):
        """send_notification should return True when disabled."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": False})

        result = agent.send_notification("Test message")

        assert result is True

    def test_send_test_email_not_enabled(self):
        """send_test_email should warn when not enabled."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({
            "enabled": True,
            "email": {"enabled": False},
        })

        result = agent.send_test_email()

        assert result is False

    def test_send_test_sms_not_enabled(self):
        """send_test_sms should warn when not enabled."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({
            "enabled": True,
            "sms": {"enabled": False},
        })

        result = agent.send_test_sms()

        assert result is False

    def test_send_test_slack_not_enabled(self):
        """send_test_slack should warn when not enabled."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({
            "enabled": True,
            "slack": {"enabled": False},
        })

        result = agent.send_test_slack()

        assert result is False

    def test_send_test_notification_by_type_email(self):
        """send_test_notification_by_type should route to email."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        with patch.object(agent, "send_test_email", return_value=True) as mock:
            agent.send_test_notification_by_type("email")
            mock.assert_called_once()

    def test_send_test_notification_by_type_sms(self):
        """send_test_notification_by_type should route to sms."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        with patch.object(agent, "send_test_sms", return_value=True) as mock:
            agent.send_test_notification_by_type("sms")
            mock.assert_called_once()

    def test_send_test_notification_by_type_slack(self):
        """send_test_notification_by_type should route to slack."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        with patch.object(agent, "send_test_slack", return_value=True) as mock:
            agent.send_test_notification_by_type("slack")
            mock.assert_called_once()

    def test_send_test_notification_by_type_unknown(self):
        """send_test_notification_by_type should handle unknown type."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        result = agent.send_test_notification_by_type("unknown_type")

        assert result is False


class TestNotificationAgentMessagePreparation:
    """Tests for message preparation methods."""

    def test_prepare_message_content(self):
        """_prepare_message_content should create all message formats."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        content = agent._prepare_message_content(
            message="Test message",
            subject="Test Subject",
            notification_type="info",
        )

        assert "subject" in content
        assert "body" in content
        assert "sms" in content
        assert "slack" in content
        assert content["subject"] == "Test Subject"
        assert "Test message" in content["body"]

    def test_prepare_message_content_with_stats(self):
        """_prepare_message_content should include stats when provided."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": True})

        stats = {"total_scraped": 100, "errors": 5}
        content = agent._prepare_message_content(
            message="Completed",
            subject="Report",
            notification_type="success",
            stats=stats,
        )

        assert "100" in content["body"] or "total" in content["body"].lower()


class TestNotificationAgentColors:
    """Tests for color mapping."""

    def test_get_color_for_type_success(self):
        """_get_color_for_type should return green for success."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        color = agent._get_color_for_type("success")

        assert color == "good"

    def test_get_color_for_type_warning(self):
        """_get_color_for_type should return warning color."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        color = agent._get_color_for_type("warning")

        assert color == "warning"

    def test_get_color_for_type_error(self):
        """_get_color_for_type should return danger for error."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        color = agent._get_color_for_type("error")

        assert color == "danger"

    def test_get_color_for_type_unknown(self):
        """_get_color_for_type should return default for unknown type."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        color = agent._get_color_for_type("unknown")

        assert color == "#36a64f"  # Default green


class TestNotificationAgentFormatting:
    """Tests for formatting methods."""

    def test_format_stats_for_email(self):
        """_format_stats_for_email should format stats nicely."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        stats = {"total_records": 100, "success_rate": 95.5}
        formatted = agent._format_stats_for_email(stats)

        assert "Total Records" in formatted
        assert "100" in formatted
        assert "Success Rate" in formatted

    def test_format_stats_for_slack(self):
        """_format_stats_for_slack should create Slack fields."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({})

        stats = {"total": 50, "errors": 2}
        fields = agent._format_stats_for_slack(stats)

        assert isinstance(fields, list)
        assert len(fields) == 2
        assert all("title" in f and "value" in f for f in fields)


class TestNotificationAgentCompletionNotifications:
    """Tests for completion notification methods."""

    def test_send_completion_notification_success(self):
        """send_completion_notification should format success message."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": False})

        result = agent.send_completion_notification(
            session_name="test_session",
            stats={"total": 100},
            success=True,
        )

        # Should return True when notifications disabled
        assert result is True

    def test_send_completion_notification_failure(self):
        """send_completion_notification should format failure message."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": False})

        result = agent.send_completion_notification(
            session_name="test_session",
            stats={"total": 50, "errors": 10},
            success=False,
        )

        assert result is True

    def test_send_error_notification(self):
        """send_error_notification should include error details."""
        from src.notification_agent import NotificationAgent

        agent = NotificationAgent({"enabled": False})

        result = agent.send_error_notification(
            session_name="test_session",
            error_message="Connection timeout",
            error_details="Failed after 3 retries",
        )

        assert result is True


class TestCreateSampleNotificationConfig:
    """Tests for sample config creation."""

    def test_create_sample_notification_config(self):
        """create_sample_notification_config should return valid structure."""
        from src.notification_agent import create_sample_notification_config

        config = create_sample_notification_config()

        assert "enabled" in config
        assert config["enabled"] is False
        assert "email" in config
        assert "sms" in config
        assert "slack" in config

    def test_sample_config_email_structure(self):
        """Sample config email section should have all required fields."""
        from src.notification_agent import create_sample_notification_config

        config = create_sample_notification_config()

        email_config = config["email"]
        assert "smtp_server" in email_config
        assert "smtp_port" in email_config
        assert "sender_email" in email_config
        assert "recipients" in email_config

    def test_sample_config_sms_structure(self):
        """Sample config SMS section should have Twilio fields."""
        from src.notification_agent import create_sample_notification_config

        config = create_sample_notification_config()

        sms_config = config["sms"]
        assert "twilio_account_sid" in sms_config
        assert "twilio_auth_token" in sms_config
        assert "from_number" in sms_config
        assert "to_numbers" in sms_config
