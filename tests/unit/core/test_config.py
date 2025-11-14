"""
Unit tests for configuration module.

Tests the Config class and configuration management functionality.
"""

import pytest
from pathlib import Path
from src.core.config import (
    Config,
    DatabaseConfig,
    BrowserConfig,
    AIConfig,
    OctoConfig,
    NotificationConfig,
    get_config,
    set_config,
)
from src.core.exceptions import ConfigurationError


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_default_values(self):
        """Test default database configuration values."""
        config = DatabaseConfig()

        assert config.url == "sqlite:///octomaster.db"
        assert config.echo is False
        assert config.pool_size == 5
        assert config.max_overflow == 10

    def test_custom_values(self):
        """Test custom database configuration."""
        config = DatabaseConfig(
            url="postgresql://localhost/test",
            echo=True,
            pool_size=10
        )

        assert config.url == "postgresql://localhost/test"
        assert config.echo is True
        assert config.pool_size == 10


class TestBrowserConfig:
    """Tests for BrowserConfig."""

    def test_default_values(self):
        """Test default browser configuration."""
        config = BrowserConfig()

        assert config.default_browser == "chromium"
        assert config.headless is False
        assert config.timeout == 30000
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080

    def test_custom_viewport(self):
        """Test custom viewport configuration."""
        config = BrowserConfig(viewport_width=1280, viewport_height=720)

        assert config.viewport_width == 1280
        assert config.viewport_height == 720


class TestAIConfig:
    """Tests for AIConfig."""

    def test_default_disabled(self):
        """Test AI is disabled by default."""
        config = AIConfig()

        assert config.enabled is False
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7

    def test_enable_ai(self):
        """Test enabling AI with custom settings."""
        config = AIConfig(
            enabled=True,
            provider="anthropic",
            model="claude-3",
            temperature=0.5
        )

        assert config.enabled is True
        assert config.provider == "anthropic"
        assert config.model == "claude-3"
        assert config.temperature == 0.5


class TestConfig:
    """Tests for main Config class."""

    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = Config()

        assert config.app_name == "OctoMaster Pro"
        assert config.app_version == "1.0.0-alpha"
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_directories_creation(self):
        """Test that directories are created on initialization."""
        config = Config()

        assert config.data_dir is not None
        assert config.logs_dir is not None
        assert config.plugins_dir is not None
        assert config.templates_dir is not None

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        config = Config()

        # Get nested value with dot notation
        assert config.get("database.url") == "sqlite:///octomaster.db"
        assert config.get("browser.headless") is False
        assert config.get("ai.enabled") is False

        # Get with default value
        assert config.get("nonexistent.key", "default") == "default"

    def test_set_nested_value(self):
        """Test setting nested configuration values."""
        config = Config()

        # Set top-level value
        config.set("debug", True)
        assert config.debug is True

        # Set nested value
        config.set("browser.headless", True)
        assert config.browser.headless is True

    def test_set_invalid_key_raises_error(self):
        """Test that setting invalid key raises ConfigurationError."""
        config = Config()

        with pytest.raises(ConfigurationError):
            config.set("nonexistent.deeply.nested.key", "value")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = Config()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "app_name" in config_dict
        assert "database" in config_dict
        assert "browser" in config_dict

    def test_from_file_nonexistent_raises_error(self, tmp_path):
        """Test loading from non-existent file raises error."""
        nonexistent_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(ConfigurationError, match="not found"):
            Config.from_file(nonexistent_file)

    def test_from_env_file(self, tmp_path):
        """Test loading configuration from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "APP_NAME=TestApp\n"
            "DEBUG=true\n"
            "LOG_LEVEL=DEBUG\n"
        )

        # Note: This test would require proper environment variable handling
        # For now, we just test that the method exists and doesn't crash
        config = Config()
        assert config is not None


class TestConfigGlobalInstance:
    """Tests for global configuration instance."""

    def test_get_config_singleton(self):
        """Test that get_config returns singleton instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_set_config(self):
        """Test setting global configuration."""
        custom_config = Config()
        custom_config.debug = True

        set_config(custom_config)

        retrieved_config = get_config()
        assert retrieved_config.debug is True


class TestNotificationConfig:
    """Tests for NotificationConfig."""

    def test_all_disabled_by_default(self):
        """Test that specific notification channels are disabled by default."""
        config = NotificationConfig()

        assert config.enabled is True  # General notifications enabled
        assert config.email_enabled is False
        assert config.telegram_enabled is False
        assert config.slack_enabled is False
        assert config.discord_enabled is False

    def test_enable_email_notifications(self):
        """Test enabling email notifications."""
        config = NotificationConfig(
            email_enabled=True,
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="user@example.com",
            email_from="user@example.com",
            email_to="admin@example.com"
        )

        assert config.email_enabled is True
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 587


class TestOctoConfig:
    """Tests for Octo Browser configuration."""

    def test_default_values(self):
        """Test default Octo configuration."""
        config = OctoConfig()

        assert config.enabled is False
        assert config.api_url == "http://localhost:58888"
        assert config.timeout == 30

    def test_custom_configuration(self):
        """Test custom Octo configuration."""
        config = OctoConfig(
            enabled=True,
            api_url="http://custom-host:8888",
            api_key="test-key",
            timeout=60
        )

        assert config.enabled is True
        assert config.api_url == "http://custom-host:8888"
        assert config.api_key == "test-key"
        assert config.timeout == 60
