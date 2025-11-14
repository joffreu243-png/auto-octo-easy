"""
Configuration management for OctoMaster Pro.

This module provides comprehensive configuration management using Pydantic,
supporting environment variables, config files, and runtime configuration.
"""

import os
from pathlib import Path
from typing import Optional, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.exceptions import ConfigurationError


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    url: str = Field(default="sqlite:///octomaster.db", description="Database URL")
    echo: bool = Field(default=False, description="Echo SQL queries")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")

    model_config = SettingsConfigDict(env_prefix="DB_")


class BrowserConfig(BaseSettings):
    """Browser automation configuration."""

    default_browser: str = Field(default="chromium", description="Default browser")
    headless: bool = Field(default=False, description="Run in headless mode")
    timeout: int = Field(default=30000, description="Default timeout in ms")
    viewport_width: int = Field(default=1920, description="Viewport width")
    viewport_height: int = Field(default=1080, description="Viewport height")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")

    # WebEngine settings (for embedded browser)
    webengine_gpu_enabled: bool = Field(default=False, description="Enable GPU for WebEngine")
    webengine_js_enabled: bool = Field(default=True, description="Enable JavaScript")

    model_config = SettingsConfigDict(env_prefix="BROWSER_")


class AIConfig(BaseSettings):
    """AI assistant configuration."""

    enabled: bool = Field(default=False, description="Enable AI assistant")
    provider: str = Field(default="openai", description="AI provider (openai, anthropic)")
    api_key: Optional[str] = Field(default=None, description="AI API key")
    model: str = Field(default="gpt-4", description="AI model to use")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=2000, description="Max tokens in response")

    model_config = SettingsConfigDict(env_prefix="AI_")


class OctoConfig(BaseSettings):
    """Octo Browser integration configuration."""

    enabled: bool = Field(default=False, description="Enable Octo integration")
    api_url: str = Field(default="http://localhost:58888", description="Octo API URL")
    api_key: Optional[str] = Field(default=None, description="Octo API key")
    timeout: int = Field(default=30, description="API timeout in seconds")

    model_config = SettingsConfigDict(env_prefix="OCTO_")


class NotificationConfig(BaseSettings):
    """Notification settings."""

    enabled: bool = Field(default=True, description="Enable notifications")

    # Email
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    email_from: Optional[str] = Field(default=None, description="From email address")
    email_to: Optional[str] = Field(default=None, description="To email address")

    # Telegram
    telegram_enabled: bool = Field(default=False, description="Enable Telegram notifications")
    telegram_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID")

    # Slack
    slack_enabled: bool = Field(default=False, description="Enable Slack notifications")
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack webhook URL")

    # Discord
    discord_enabled: bool = Field(default=False, description="Enable Discord notifications")
    discord_webhook_url: Optional[str] = Field(default=None, description="Discord webhook URL")

    model_config = SettingsConfigDict(env_prefix="NOTIFY_")


class Config(BaseSettings):
    """Main application configuration."""

    # Application settings
    app_name: str = Field(default="OctoMaster Pro", description="Application name")
    app_version: str = Field(default="1.0.0-alpha", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Directories
    base_dir: Path = Field(default_factory=lambda: Path.cwd(), description="Base directory")
    data_dir: Optional[Path] = Field(default=None, description="Data directory")
    logs_dir: Optional[Path] = Field(default=None, description="Logs directory")
    plugins_dir: Optional[Path] = Field(default=None, description="Plugins directory")
    templates_dir: Optional[Path] = Field(default=None, description="Templates directory")

    # Feature flags
    enable_recorder: bool = Field(default=True, description="Enable action recorder")
    enable_ai: bool = Field(default=False, description="Enable AI assistant")
    enable_plugins: bool = Field(default=True, description="Enable plugin system")
    enable_scheduler: bool = Field(default=True, description="Enable task scheduler")

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    octo: OctoConfig = Field(default_factory=OctoConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize configuration."""
        super().__init__(**kwargs)
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Setup application directories."""
        # Set default directories if not specified
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.logs_dir is None:
            self.logs_dir = self.base_dir / "logs"
        if self.plugins_dir is None:
            self.plugins_dir = self.base_dir / "plugins"
        if self.templates_dir is None:
            self.templates_dir = self.base_dir / "templates"

        # Create directories if they don't exist
        for directory in [self.data_dir, self.logs_dir, self.plugins_dir, self.templates_dir]:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'database.url')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            keys = key.split(".")
            value: Any = self
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
            return value
        except Exception:
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set

        Raises:
            ConfigurationError: If key is invalid
        """
        try:
            keys = key.split(".")
            if len(keys) == 1:
                setattr(self, keys[0], value)
            else:
                obj: Any = self
                for k in keys[:-1]:
                    obj = getattr(obj, k)
                setattr(obj, keys[-1], value)
        except Exception as e:
            raise ConfigurationError(f"Failed to set config key '{key}': {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return self.model_dump()

    @classmethod
    def from_file(cls, file_path: Path) -> "Config":
        """
        Load configuration from file.

        Args:
            file_path: Path to configuration file (.env, .yaml, .json)

        Returns:
            Config instance

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        try:
            if file_path.suffix == ".env":
                # Load from .env file
                return cls(_env_file=str(file_path))
            elif file_path.suffix in [".yaml", ".yml"]:
                import yaml
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                return cls(**data)
            elif file_path.suffix == ".json":
                import json
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            else:
                raise ConfigurationError(f"Unsupported file format: {file_path.suffix}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {e}") from e


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """
    Set global configuration instance.

    Args:
        config: Config instance to set
    """
    global _config
    _config = config
