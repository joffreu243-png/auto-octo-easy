"""
Notification Manager for managing multiple notification channels.
"""

from typing import Dict, List, Optional
from loguru import logger

from octomaster.integrations.notifications.channels import (
    NotificationChannel,
    EmailChannel,
    TelegramChannel,
    SlackChannel,
    DiscordChannel,
    DesktopChannel,
)


class NotificationManager:
    """
    Manages multiple notification channels.

    Features:
    - Multiple channels support
    - Channel priority
    - Fallback mechanism
    - Message templates
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize notification manager.

        Args:
            config: Configuration dictionary with channel settings
        """
        self.config = config or {}
        self.channels: Dict[str, NotificationChannel] = {}

        # Initialize channels from config
        self._initialize_channels()

    def _initialize_channels(self):
        """Initialize notification channels from configuration."""
        # Email channel
        if self.config.get("email", {}).get("enabled"):
            self.channels["email"] = EmailChannel(self.config["email"])
            logger.info("Email channel initialized")

        # Telegram channel
        if self.config.get("telegram", {}).get("enabled"):
            self.channels["telegram"] = TelegramChannel(self.config["telegram"])
            logger.info("Telegram channel initialized")

        # Slack channel
        if self.config.get("slack", {}).get("enabled"):
            self.channels["slack"] = SlackChannel(self.config["slack"])
            logger.info("Slack channel initialized")

        # Discord channel
        if self.config.get("discord", {}).get("enabled"):
            self.channels["discord"] = DiscordChannel(self.config["discord"])
            logger.info("Discord channel initialized")

        # Desktop channel
        if self.config.get("desktop", {}).get("enabled", True):
            self.channels["desktop"] = DesktopChannel(self.config.get("desktop", {}))
            logger.info("Desktop channel initialized")

    def add_channel(self, name: str, channel: NotificationChannel):
        """Add a custom notification channel."""
        self.channels[name] = channel
        logger.info(f"Added channel: {name}")

    def remove_channel(self, name: str):
        """Remove a notification channel."""
        if name in self.channels:
            del self.channels[name]
            logger.info(f"Removed channel: {name}")

    async def send(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """
        Send notification to specified channels.

        Args:
            title: Notification title
            message: Notification message
            channels: List of channel names (if None, send to all enabled)
            **kwargs: Additional parameters for channels

        Returns:
            Dictionary with results for each channel
        """
        # Determine which channels to use
        if channels is None:
            channels = list(self.channels.keys())

        results = {}

        for channel_name in channels:
            if channel_name not in self.channels:
                logger.warning(f"Channel not found: {channel_name}")
                results[channel_name] = False
                continue

            channel = self.channels[channel_name]

            if not channel.is_enabled():
                logger.debug(f"Channel disabled: {channel_name}")
                results[channel_name] = False
                continue

            try:
                success = await channel.send(title, message, **kwargs)
                results[channel_name] = success
            except Exception as e:
                logger.error(f"Error sending to {channel_name}: {e}")
                results[channel_name] = False

        return results

    async def send_success(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """Send success notification."""
        full_title = f"✅ {title}"
        return await self.send(full_title, message, channels, **kwargs)

    async def send_error(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """Send error notification."""
        full_title = f"❌ {title}"
        return await self.send(full_title, message, channels, **kwargs)

    async def send_warning(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """Send warning notification."""
        full_title = f"⚠️ {title}"
        return await self.send(full_title, message, channels, **kwargs)

    async def send_info(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """Send info notification."""
        full_title = f"ℹ️ {title}"
        return await self.send(full_title, message, channels, **kwargs)

    def get_enabled_channels(self) -> List[str]:
        """Get list of enabled channel names."""
        return [name for name, channel in self.channels.items() if channel.is_enabled()]

    def __repr__(self) -> str:
        enabled = len(self.get_enabled_channels())
        return f"NotificationManager(channels={len(self.channels)}, enabled={enabled})"
