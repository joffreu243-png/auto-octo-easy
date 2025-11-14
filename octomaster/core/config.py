"""
Configuration management for OctoMaster Pro.
"""

import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class Config:
    """Application configuration."""

    # Application
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "OctoMaster Pro"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "0.1.0-alpha"))
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Paths
    project_root: Path = field(default_factory=lambda: Path.cwd())
    logs_dir: Path = field(init=False)
    screenshots_dir: Path = field(init=False)
    downloads_dir: Path = field(init=False)
    projects_dir: Path = field(init=False)
    temp_dir: Path = field(init=False)

    # Octo Browser API
    octo_api_url: str = field(
        default_factory=lambda: os.getenv("OCTO_API_URL", "https://api.octobrowser.net")
    )
    octo_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OCTO_API_KEY"))
    octo_local_api_port: int = field(
        default_factory=lambda: int(os.getenv("OCTO_LOCAL_API_PORT", "58888"))
    )

    # AI Configuration
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    )
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    use_local_llm: bool = field(
        default_factory=lambda: os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    )

    # Database
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./octomaster.db")
    )

    # Browser Settings
    default_browser: str = field(
        default_factory=lambda: os.getenv("DEFAULT_BROWSER", "chromium")
    )
    headless: bool = field(
        default_factory=lambda: os.getenv("HEADLESS", "false").lower() == "true"
    )
    browser_timeout: int = field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30000"))
    )

    # Features
    enable_ai_assistant: bool = field(
        default_factory=lambda: os.getenv("ENABLE_AI_ASSISTANT", "true").lower() == "true"
    )
    enable_recorder: bool = field(
        default_factory=lambda: os.getenv("ENABLE_RECORDER", "true").lower() == "true"
    )
    enable_cloud_sync: bool = field(
        default_factory=lambda: os.getenv("ENABLE_CLOUD_SYNC", "false").lower() == "true"
    )

    # Notifications
    telegram_enabled: bool = field(
        default_factory=lambda: os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    )
    telegram_bot_token: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN")
    )
    telegram_chat_id: Optional[str] = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID"))

    # Performance
    max_workers: int = field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "4")))
    cache_enabled: bool = field(
        default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true"
    )

    def __post_init__(self):
        """Initialize derived paths."""
        self.logs_dir = self.project_root / "logs"
        self.screenshots_dir = self.project_root / "screenshots"
        self.downloads_dir = self.project_root / "downloads"
        self.projects_dir = self.project_root / "projects"
        self.temp_dir = self.project_root / "temp"

        # Create directories
        for directory in [
            self.logs_dir,
            self.screenshots_dir,
            self.downloads_dir,
            self.projects_dir,
            self.temp_dir,
        ]:
            directory.mkdir(exist_ok=True)

        logger.debug("Configuration initialized")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        setattr(self, key, value)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "app_env": self.app_env,
            "debug": self.debug,
            "default_browser": self.default_browser,
            "headless": self.headless,
            "enable_ai_assistant": self.enable_ai_assistant,
            "enable_recorder": self.enable_recorder,
        }
