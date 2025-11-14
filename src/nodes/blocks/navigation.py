"""
Navigation blocks for browser automation.

Blocks for page navigation: open URL, back, forward, refresh, etc.
"""

from typing import Dict, Any
from loguru import logger

from src.nodes.blocks.base import BaseBlock


class OpenURLBlock(BaseBlock):
    """Open URL in browser."""

    def __init__(self) -> None:
        """Initialize OpenURL block."""
        super().__init__(
            title="Open URL",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("url", "https://example.com")
        self.set_param("wait_until", "domcontentloaded")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute open URL action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            url = self.get_param("url")
            wait_until = self.get_param("wait_until", "domcontentloaded")

            logger.info(f"Opening URL: {url}")

            result = await browser.navigate(url, wait_until=wait_until)

            if result.success:
                self._executed = True
                self._result = {"url": url, "success": True}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Navigation failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"OpenURL block error: {e}")
            raise


class BackBlock(BaseBlock):
    """Navigate back in browser history."""

    def __init__(self) -> None:
        """Initialize Back block."""
        super().__init__(
            title="Go Back",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute go back action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            logger.info("Going back")

            await browser.go_back()

            self._executed = True
            self._result = {"success": True}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Back block error: {e}")
            raise


class ForwardBlock(BaseBlock):
    """Navigate forward in browser history."""

    def __init__(self) -> None:
        """Initialize Forward block."""
        super().__init__(
            title="Go Forward",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute go forward action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            logger.info("Going forward")

            await browser.go_forward()

            self._executed = True
            self._result = {"success": True}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Forward block error: {e}")
            raise


class RefreshBlock(BaseBlock):
    """Refresh current page."""

    def __init__(self) -> None:
        """Initialize Refresh block."""
        super().__init__(
            title="Refresh Page",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute refresh action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            logger.info("Refreshing page")

            await browser.reload()

            self._executed = True
            self._result = {"success": True}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Refresh block error: {e}")
            raise


class NewTabBlock(BaseBlock):
    """Create new browser tab."""

    def __init__(self) -> None:
        """Initialize NewTab block."""
        super().__init__(
            title="New Tab",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute new tab action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            logger.info("Creating new tab")

            page = await browser.new_tab()

            self._executed = True
            self._result = {"success": True, "page": page}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"NewTab block error: {e}")
            raise


class CloseTabBlock(BaseBlock):
    """Close current browser tab."""

    def __init__(self) -> None:
        """Initialize CloseTab block."""
        super().__init__(
            title="Close Tab",
            block_type="navigation",
            num_inputs=1,
            num_outputs=1,
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute close tab action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            logger.info("Closing tab")

            await browser.close_tab()

            self._executed = True
            self._result = {"success": True}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"CloseTab block error: {e}")
            raise
