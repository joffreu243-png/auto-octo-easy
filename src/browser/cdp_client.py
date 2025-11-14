"""
Chrome DevTools Protocol client for OctoMaster Pro.

Provides low-level CDP access for advanced browser control.
"""

from typing import Optional, Dict, Any, Callable
import json
import asyncio
from loguru import logger

from playwright.async_api import CDPSession, Page


class CDPClient:
    """Chrome DevTools Protocol client."""

    def __init__(self, page: Page) -> None:
        """Initialize CDP client.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self._session: Optional[CDPSession] = None
        self._event_handlers: Dict[str, list[Callable]] = {}

    async def connect(self) -> bool:
        """Connect to CDP session.

        Returns:
            True if connected successfully
        """
        try:
            logger.info("Connecting to CDP session")
            self._session = await self.page.context.new_cdp_session(self.page)
            logger.info("CDP session connected")
            return True
        except Exception as e:
            logger.error(f"CDP connection failed: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect CDP session."""
        if self._session:
            try:
                await self._session.detach()
                self._session = None
                logger.info("CDP session disconnected")
            except Exception as e:
                logger.error(f"CDP disconnect error: {e}")

    async def send(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send CDP command.

        Args:
            method: CDP method name
            params: Method parameters

        Returns:
            Command result
        """
        if not self._session:
            raise RuntimeError("CDP session not connected")

        try:
            result = await self._session.send(method, params or {})
            logger.debug(f"CDP command sent: {method}")
            return result
        except Exception as e:
            logger.error(f"CDP command failed ({method}): {e}")
            raise

    def on(self, event: str, handler: Callable) -> None:
        """Register CDP event handler.

        Args:
            event: CDP event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
            if self._session:
                self._session.on(event, lambda data: self._emit_event(event, data))

        self._event_handlers[event].append(handler)

    def _emit_event(self, event: str, data: Any) -> None:
        """Emit event to handlers.

        Args:
            event: Event name
            data: Event data
        """
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"CDP event handler error ({event}): {e}")

    async def enable_console(self) -> None:
        """Enable console API."""
        await self.send("Runtime.enable")
        await self.send("Console.enable")

    async def enable_network(self) -> None:
        """Enable network monitoring."""
        await self.send("Network.enable")

    async def enable_page(self) -> None:
        """Enable page domain."""
        await self.send("Page.enable")

    async def set_user_agent(self, user_agent: str) -> None:
        """Set custom user agent.

        Args:
            user_agent: User agent string
        """
        await self.send("Network.setUserAgentOverride", {"userAgent": user_agent})

    async def emulate_network_conditions(
        self,
        offline: bool = False,
        latency: int = 0,
        download_throughput: int = -1,
        upload_throughput: int = -1,
    ) -> None:
        """Emulate network conditions.

        Args:
            offline: Emulate offline mode
            latency: Additional latency (ms)
            download_throughput: Download speed (bytes/sec, -1 = unlimited)
            upload_throughput: Upload speed (bytes/sec, -1 = unlimited)
        """
        await self.send("Network.emulateNetworkConditions", {
            "offline": offline,
            "latency": latency,
            "downloadThroughput": download_throughput,
            "uploadThroughput": upload_throughput,
        })

    async def capture_screenshot(
        self,
        format: str = "png",
        quality: Optional[int] = None,
    ) -> bytes:
        """Capture screenshot via CDP.

        Args:
            format: Image format (png or jpeg)
            quality: JPEG quality (0-100)

        Returns:
            Screenshot data
        """
        params = {"format": format}
        if quality and format == "jpeg":
            params["quality"] = quality

        result = await self.send("Page.captureScreenshot", params)
        import base64
        return base64.b64decode(result["data"])
