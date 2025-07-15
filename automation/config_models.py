"""
Configuration Models with Pydantic Validation

This module defines validated configuration models for the automation system,
replacing the previous unvalidated YAML loading with type-safe configuration.
"""

import os
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class ScheduleConfig(BaseModel):
    """Configuration for scheduled tasks."""

    frequency: Literal["hourly", "daily", "weekly"] = Field(description="How often the task should run")
    time: Optional[str] = Field(default=None, description="Time to run (HH:MM format for daily/weekly)")
    day: Optional[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]] = Field(
        default=None, description="Day of week for weekly tasks"
    )

    @validator("time")
    def validate_time_format(cls, v):
        """Validate time format."""
        if v is not None:
            import re

            if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
                raise ValueError("Time must be in HH:MM format")
        return v

    @validator("time")
    def validate_time_required(cls, v, values):
        """Validate that time is provided for daily and weekly schedules."""
        if values.get("frequency") in ["daily", "weekly"] and not v:
            raise ValueError("Time is required for daily and weekly schedules")
        return v

    @validator("day")
    def validate_day_for_weekly(cls, v, values):
        """Validate that day is provided for weekly schedules."""
        if values.get("frequency") == "weekly" and not v:
            raise ValueError("Day is required for weekly schedules")
        return v


class SchedulesConfig(BaseModel):
    """All scheduled task configurations."""

    scraping: ScheduleConfig = Field(default_factory=lambda: ScheduleConfig(frequency="daily", time="02:00"))
    validation: ScheduleConfig = Field(default_factory=lambda: ScheduleConfig(frequency="daily", time="06:00"))
    export: ScheduleConfig = Field(
        default_factory=lambda: ScheduleConfig(frequency="weekly", time="23:00", day="sunday")
    )
    dashboard_update: ScheduleConfig = Field(default_factory=lambda: ScheduleConfig(frequency="hourly"))
    list_discovery: ScheduleConfig = Field(default_factory=lambda: ScheduleConfig(frequency="hourly"))


class MonitoringConfig(BaseModel):
    """Configuration for file monitoring."""

    input_directories: List[str] = Field(
        default=["input/", "snapshots/"], description="Directories to monitor for new files"
    )
    file_patterns: List[str] = Field(default=["*.json", "*.csv", "*.html"], description="File patterns to watch for")
    auto_process: bool = Field(default=True, description="Automatically process new files")
    batch_delay: int = Field(default=300, description="Delay before processing batch (seconds)", ge=0, le=3600)


class EmailConfig(BaseModel):
    """Email notification configuration."""

    enabled: bool = Field(default=False)
    smtp_server: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587, ge=1, le=65535)
    username: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    recipients: List[EmailStr] = Field(default_factory=list)

    @validator("smtp_server")
    def validate_smtp_server_when_enabled(cls, v, values):
        """Validate SMTP server is provided when email is enabled."""
        if values.get("enabled") and not v:
            raise ValueError("smtp_server is required when email is enabled")
        return v

    @validator("username")
    def validate_username_when_enabled(cls, v, values):
        """Validate username is provided when email is enabled."""
        if values.get("enabled") and not v:
            raise ValueError("username is required when email is enabled")
        return v

    @validator("password")
    def validate_password_when_enabled(cls, v, values):
        """Validate password is provided when email is enabled."""
        if values.get("enabled") and not v:
            raise ValueError("password is required when email is enabled")
        return v


class NotificationsConfig(BaseModel):
    """Notification system configuration."""

    discord_webhook: Optional[HttpUrl] = Field(default=None)
    email: EmailConfig = Field(default_factory=EmailConfig)


class GoogleSheetsConfig(BaseModel):
    """Google Sheets integration configuration."""

    enabled: bool = Field(default=False)
    spreadsheet_id: Optional[str] = Field(default=None)
    credentials_path: Optional[str] = Field(default=None)

    @validator("spreadsheet_id")
    def validate_spreadsheet_id_when_enabled(cls, v, values):
        """Validate spreadsheet ID is provided when Google Sheets is enabled."""
        if values.get("enabled") and not v:
            raise ValueError("spreadsheet_id is required when Google Sheets is enabled")
        return v

    @validator("credentials_path")
    def validate_credentials_path_when_enabled(cls, v, values):
        """Validate credentials path is provided and exists when Google Sheets is enabled."""
        if values.get("enabled"):
            if not v:
                raise ValueError("credentials_path is required when Google Sheets is enabled")
            if not os.path.exists(v):
                raise ValueError(f"Credentials file not found: {v}")
        return v


class LocalHtmlConfig(BaseModel):
    """Local HTML dashboard configuration."""

    enabled: bool = Field(default=True)
    output_path: str = Field(default="output/dashboard.html")


class DashboardConfig(BaseModel):
    """Dashboard configuration."""

    google_sheets: GoogleSheetsConfig = Field(default_factory=GoogleSheetsConfig)
    local_html: LocalHtmlConfig = Field(default_factory=LocalHtmlConfig)


class PipelineConfig(BaseModel):
    """Pipeline execution configuration."""

    sites: List[str] = Field(default_factory=list, description="Target sites to process")
    default_flags: List[str] = Field(
        default_factory=lambda: ["--schema-matrix", "--emit-status", "--emit-drift-dashboard"],
        description="Default flags for pipeline execution",
    )
    timeout: int = Field(
        default=3600,
        description="Execution timeout in seconds",
        ge=60,  # Minimum 1 minute
        le=86400,  # Maximum 24 hours
    )
    retry_count: int = Field(default=3, description="Number of retry attempts on failure", ge=0, le=10)


class AutomationConfig(BaseModel):
    """Complete automation configuration with validation."""

    schedules: SchedulesConfig = Field(default_factory=SchedulesConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)

    class Config:
        """Pydantic configuration."""

        # Allow environment variables to override config values
        env_prefix = "AUTOMATION_"
        # Validate assignment to catch errors early
        validate_assignment = True
        # Use enum values for better validation
        use_enum_values = True


class ListDiscoveryConfig(BaseModel):
    """Configuration for the list discovery agent."""

    class UrlConfig(BaseModel):
        """URL configuration for monitoring."""

        url: HttpUrl
        name: str = Field(description="Human-readable name for the URL")
        check_interval: int = Field(
            default=3600,
            description="Check interval in seconds",
            ge=60,  # Minimum 1 minute
            le=86400,  # Maximum 24 hours
        )
        enabled: bool = Field(default=True)

    class SecurityConfig(BaseModel):
        """Security and rate limiting configuration."""

        user_agent: str = Field(
            default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            description="User agent string for requests",
        )
        request_timeout: int = Field(default=30, description="Request timeout in seconds", ge=5, le=300)
        rate_limit_delay: float = Field(default=1.0, description="Delay between requests in seconds", ge=0.1, le=60.0)
        max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0, le=10)

    class FileTypesConfig(BaseModel):
        """File types to monitor."""

        documents: List[str] = Field(
            default=["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"],
            description="Document file extensions to monitor",
        )
        images: List[str] = Field(
            default=["jpg", "jpeg", "png", "gif", "bmp", "svg"], description="Image file extensions to monitor"
        )
        archives: List[str] = Field(
            default=["zip", "rar", "7z", "tar", "gz"], description="Archive file extensions to monitor"
        )
        data: List[str] = Field(default=["json", "csv", "xml", "txt"], description="Data file extensions to monitor")

    urls: List[UrlConfig] = Field(default_factory=list, description="URLs to monitor")
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    file_types: FileTypesConfig = Field(default_factory=FileTypesConfig)
    output_directory: str = Field(default="output/list_discovery", description="Output directory for discovered files")

    class Config:
        """Pydantic configuration."""

        env_prefix = "LIST_DISCOVERY_"
        validate_assignment = True
