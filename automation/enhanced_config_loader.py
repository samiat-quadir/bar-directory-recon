"""
Enhanced Configuration Loader with Environment Variable Support

This module provides secure configuration loading with:
- Environment variable substitution
- Pydantic validation
- Encrypted credential support
- Default value handling
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import ValidationError

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from .config_models import AutomationConfig, ListDiscoveryConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Enhanced configuration loader with validation and environment support."""

    def __init__(self, dotenv_path: Optional[str] = None):
        """Initialize the config loader.

        Args:
            dotenv_path: Path to .env file (optional)
        """
        self.dotenv_path = dotenv_path
        self._load_environment()

    def _load_environment(self) -> None:
        """Load environment variables from .env file if available."""
        if DOTENV_AVAILABLE and self.dotenv_path and Path(self.dotenv_path).exists():
            load_dotenv(self.dotenv_path)
            logger.info(f"Loaded environment variables from {self.dotenv_path}")
        elif DOTENV_AVAILABLE:
            # Try to load from common locations
            common_env_files = [".env", ".env.local", ".env.work"]
            for env_file in common_env_files:
                if Path(env_file).exists():
                    load_dotenv(env_file)
                    logger.info(f"Loaded environment variables from {env_file}")
                    break

    def _substitute_env_vars(self, data: Any) -> Any:
        """Recursively substitute environment variables in configuration data.

        Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.
        """
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._substitute_string_env_vars(data)
        else:
            return data

    def _substitute_string_env_vars(self, text: str) -> str:
        """Substitute environment variables in a string."""
        import re

        # Pattern for ${VAR} or ${VAR:default}
        pattern = r"\$\{([A-Z_][A-Z0-9_]*?)(?::([^}]*))?\}"

        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""

            # Get environment variable or use default
            value = os.environ.get(var_name, default_value)

            # Handle special cases for boolean and numeric values
            if value.lower() in ("true", "false"):
                return value.lower()
            elif value.isdigit():
                return value
            else:
                return value

        return re.sub(pattern, replace_var, text)

    def load_automation_config(self, config_path: str = "automation/config.yaml") -> AutomationConfig:
        """Load and validate automation configuration.

        Args:
            config_path: Path to the configuration file

        Returns:
            Validated AutomationConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config validation fails
            yaml.YAMLError: If YAML parsing fails
        """
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return AutomationConfig()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)

            if raw_data is None:
                raw_data = {}

            # Substitute environment variables
            processed_data = self._substitute_env_vars(raw_data)

            # Create and validate config
            config = AutomationConfig(**processed_data)
            logger.info(f"Successfully loaded automation config from {config_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise

    def load_list_discovery_config(self, config_path: str = "list_discovery/config.yaml") -> ListDiscoveryConfig:
        """Load and validate list discovery configuration.

        Args:
            config_path: Path to the configuration file

        Returns:
            Validated ListDiscoveryConfig instance
        """
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return ListDiscoveryConfig()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)

            if raw_data is None:
                raw_data = {}

            # Substitute environment variables
            processed_data = self._substitute_env_vars(raw_data)

            # Create and validate config
            config = ListDiscoveryConfig(**processed_data)
            logger.info(f"Successfully loaded list discovery config from {config_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise

    def save_config_template(self, config_type: str = "automation", output_path: Optional[str] = None) -> str:
        """Generate a configuration template file with environment variable examples.

        Args:
            config_type: Type of config to generate ("automation" or "list_discovery")
            output_path: Where to save the template (optional)

        Returns:
            Path to the generated template file
        """
        if config_type == "automation":
            template = self._generate_automation_template()
            default_path = "automation/config.template.yaml"
        elif config_type == "list_discovery":
            template = self._generate_list_discovery_template()
            default_path = "list_discovery/config.template.yaml"
        else:
            raise ValueError(f"Unknown config type: {config_type}")

        output_file = Path(output_path or default_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(template)

        logger.info(f"Generated {config_type} config template: {output_file}")
        return str(output_file)

    def _generate_automation_template(self) -> str:
        """Generate automation configuration template."""
        return """# Universal Runner Configuration Template
# ==========================================
# This template shows how to use environment variables in your configuration.
# Copy this to config.yaml and customize as needed.

# Environment variable examples:
# Set these in your .env file or system environment:
# AUTOMATION_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
# AUTOMATION_EMAIL_ENABLED=true
# AUTOMATION_EMAIL_USERNAME=your-email@gmail.com
# AUTOMATION_EMAIL_PASSWORD=your-app-password

schedules:
  scraping:
    frequency: daily
    time: "02:00"
  validation:
    frequency: daily
    time: "06:00"
  export:
    frequency: weekly
    time: "23:00"
    day: sunday
  dashboard_update:
    frequency: hourly
  list_discovery:
    frequency: hourly

monitoring:
  input_directories:
    - "input/"
    - "snapshots/"
  file_patterns:
    - "*.json"
    - "*.csv"
    - "*.html"
  auto_process: true
  batch_delay: 300

notifications:
  # Use environment variable for security
  discord_webhook: "${AUTOMATION_DISCORD_WEBHOOK:}"

  email:
    enabled: ${AUTOMATION_EMAIL_ENABLED:false}
    smtp_server: "${AUTOMATION_EMAIL_SMTP_SERVER:smtp.gmail.com}"
    smtp_port: ${AUTOMATION_EMAIL_SMTP_PORT:587}
    username: "${AUTOMATION_EMAIL_USERNAME:}"
    password: "${AUTOMATION_EMAIL_PASSWORD:}"
    recipients:
      - "${AUTOMATION_EMAIL_RECIPIENT1:}"
      - "${AUTOMATION_EMAIL_RECIPIENT2:}"

dashboard:
  google_sheets:
    enabled: ${AUTOMATION_GOOGLE_SHEETS_ENABLED:false}
    spreadsheet_id: "${AUTOMATION_GOOGLE_SHEETS_ID:}"
    credentials_path: "${AUTOMATION_GOOGLE_SHEETS_CREDENTIALS:}"

  local_html:
    enabled: true
    output_path: "output/dashboard.html"

pipeline:
  sites:
    - "${AUTOMATION_SITE1:example-bar.com}"
    - "${AUTOMATION_SITE2:another-bar.com}"

  default_flags:
    - "--schema-matrix"
    - "--emit-status"
    - "--emit-drift-dashboard"

  timeout: ${AUTOMATION_PIPELINE_TIMEOUT:3600}
  retry_count: ${AUTOMATION_PIPELINE_RETRIES:3}
"""

    def _generate_list_discovery_template(self) -> str:
        """Generate list discovery configuration template."""
        return """# List Discovery Configuration Template
# =====================================

urls:
  - url: "${LIST_DISCOVERY_URL1:https://example.com}"
    name: "${LIST_DISCOVERY_NAME1:Example Site}"
    check_interval: ${LIST_DISCOVERY_INTERVAL1:3600}
    enabled: ${LIST_DISCOVERY_ENABLED1:true}

security:
  user_agent: "${LIST_DISCOVERY_USER_AGENT:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36}"
  request_timeout: ${LIST_DISCOVERY_TIMEOUT:30}
  rate_limit_delay: ${LIST_DISCOVERY_RATE_LIMIT:1.0}
  max_retries: ${LIST_DISCOVERY_MAX_RETRIES:3}

file_types:
  documents: ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]
  images: ["jpg", "jpeg", "png", "gif", "bmp", "svg"]
  archives: ["zip", "rar", "7z", "tar", "gz"]
  data: ["json", "csv", "xml", "txt"]

output_directory: "${LIST_DISCOVERY_OUTPUT:output/list_discovery}"
"""


# Convenience functions for backward compatibility
def load_automation_config(
    config_path: str = "automation/config.yaml", dotenv_path: Optional[str] = None
) -> AutomationConfig:
    """Load automation configuration with environment variable support."""
    loader = ConfigLoader(dotenv_path)
    return loader.load_automation_config(config_path)


def load_list_discovery_config(
    config_path: str = "list_discovery/config.yaml", dotenv_path: Optional[str] = None
) -> ListDiscoveryConfig:
    """Load list discovery configuration with environment variable support."""
    loader = ConfigLoader(dotenv_path)
    return loader.load_list_discovery_config(config_path)


def generate_config_template(config_type: str = "automation", output_path: Optional[str] = None) -> str:
    """Generate a configuration template."""
    loader = ConfigLoader()
    return loader.save_config_template(config_type, output_path)
