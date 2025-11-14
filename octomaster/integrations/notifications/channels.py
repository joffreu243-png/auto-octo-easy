"""
Notification channels for different services.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from loguru import logger


class NotificationChannel(ABC):
    """Base class for notification channels."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)

    @abstractmethod
    async def send(self, title: str, message: str, **kwargs) -> bool:
        """Send notification."""
        pass

    def is_enabled(self) -> bool:
        """Check if channel is enabled."""
        return self.enabled


class EmailChannel(NotificationChannel):
    """Email notification channel using SMTP."""

    async def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send email notification.

        Args:
            title: Email subject
            message: Email body
            **kwargs: Additional parameters (to, cc, bcc)

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            # Get SMTP settings
            smtp_host = self.config.get("smtp_host")
            smtp_port = self.config.get("smtp_port", 587)
            smtp_user = self.config.get("smtp_user")
            smtp_password = self.config.get("smtp_password")
            from_email = self.config.get("from_email", smtp_user)
            to_email = kwargs.get("to", self.config.get("to_email"))

            if not all([smtp_host, smtp_user, smtp_password, to_email]):
                logger.error("Email configuration incomplete")
                return False

            # Create message
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = title

            msg.attach(MIMEText(message, "plain"))

            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class TelegramChannel(NotificationChannel):
    """Telegram notification channel using Bot API."""

    async def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send Telegram notification.

        Args:
            title: Message title
            message: Message body
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            bot_token = self.config.get("bot_token")
            chat_id = kwargs.get("chat_id", self.config.get("chat_id"))

            if not all([bot_token, chat_id]):
                logger.error("Telegram configuration incomplete")
                return False

            # Format message
            text = f"<b>{title}</b>\n\n{message}"

            # Send via Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                    },
                )
                response.raise_for_status()

            logger.info(f"Telegram message sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False


class SlackChannel(NotificationChannel):
    """Slack notification channel using Webhook."""

    async def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send Slack notification.

        Args:
            title: Message title
            message: Message body
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            webhook_url = self.config.get("webhook_url")

            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return False

            # Create Slack message payload
            payload = {
                "text": title,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": title},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message},
                    },
                ],
            }

            # Send to Slack webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()

            logger.info(f"Slack message sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False


class DiscordChannel(NotificationChannel):
    """Discord notification channel using Webhook."""

    async def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send Discord notification.

        Args:
            title: Message title
            message: Message body
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            webhook_url = self.config.get("webhook_url")

            if not webhook_url:
                logger.error("Discord webhook URL not configured")
                return False

            # Create Discord embed
            payload = {
                "embeds": [
                    {
                        "title": title,
                        "description": message,
                        "color": kwargs.get("color", 5814783),  # Blue color
                        "timestamp": kwargs.get("timestamp"),
                    }
                ]
            }

            # Send to Discord webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()

            logger.info(f"Discord message sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return False


class DesktopChannel(NotificationChannel):
    """Desktop notification channel (system notifications)."""

    async def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send desktop notification.

        Args:
            title: Notification title
            message: Notification message
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            # Try different desktop notification libraries
            try:
                # Try plyer (cross-platform)
                from plyer import notification

                notification.notify(
                    title=title,
                    message=message,
                    app_name="OctoMaster Pro",
                    timeout=kwargs.get("timeout", 10),
                )
                logger.info(f"Desktop notification sent: {title}")
                return True

            except ImportError:
                logger.warning("plyer not installed, desktop notifications disabled")
                return False

        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False
