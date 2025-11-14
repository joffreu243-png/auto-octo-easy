"""
Notification system for OctoMaster Pro.
"""

from octomaster.integrations.notifications.manager import NotificationManager
from octomaster.integrations.notifications.channels import (
    EmailChannel,
    TelegramChannel,
    SlackChannel,
    DiscordChannel,
)

__all__ = [
    "NotificationManager",
    "EmailChannel",
    "TelegramChannel",
    "SlackChannel",
    "DiscordChannel",
]
