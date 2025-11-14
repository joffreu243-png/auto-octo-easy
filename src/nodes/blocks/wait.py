"""
Wait blocks for workflow timing and synchronization.

Blocks for waiting: fixed delay, element visibility, page load, etc.
"""

from typing import Dict, Any
import asyncio
from loguru import logger

from src.nodes.blocks.base import BaseBlock


class WaitBlock(BaseBlock):
    """Wait for fixed duration."""

    def __init__(self) -> None:
        """Initialize Wait block."""
        super().__init__(
            title="Wait",
            block_type="wait",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("duration", 1000)  # milliseconds

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            duration = self.get_param("duration", 1000)
            duration_sec = duration / 1000.0

            logger.info(f"Waiting {duration_sec} seconds")

            await asyncio.sleep(duration_sec)

            self._executed = True
            self._result = {"success": True, "duration": duration}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Wait block error: {e}")
            raise


class WaitForElementBlock(BaseBlock):
    """Wait for element to appear/be visible."""

    def __init__(self) -> None:
        """Initialize WaitForElement block."""
        super().__init__(
            title="Wait For Element",
            block_type="wait",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("state", "visible")  # visible, attached, detached, hidden
        self.set_param("timeout", 30000)  # milliseconds

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait for element action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions() if browser else None
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            state = self.get_param("state", "visible")
            timeout = self.get_param("timeout", 30000)

            logger.info(f"Waiting for element: {selector} (state: {state})")

            result = await actions.wait_for_selector(selector, state=state, timeout=timeout)

            if result.success:
                self._executed = True
                self._result = {"success": True, "selector": selector}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Wait for element failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"WaitForElement block error: {e}")
            raise


class WaitForNavigationBlock(BaseBlock):
    """Wait for page navigation to complete."""

    def __init__(self) -> None:
        """Initialize WaitForNavigation block."""
        super().__init__(
            title="Wait For Navigation",
            block_type="wait",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("wait_until", "load")  # load, domcontentloaded, networkidle
        self.set_param("timeout", 30000)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait for navigation action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            page = browser.current_page if browser else None
            if not page:
                raise Exception("No active page")

            wait_until = self.get_param("wait_until", "load")
            timeout = self.get_param("timeout", 30000)

            logger.info(f"Waiting for navigation (wait_until: {wait_until})")

            # Wait for load state
            await page.wait_for_load_state(wait_until, timeout=timeout)

            self._executed = True
            self._result = {"success": True}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"WaitForNavigation block error: {e}")
            raise


class WaitForSelectorBlock(BaseBlock):
    """Wait for selector to match condition."""

    def __init__(self) -> None:
        """Initialize WaitForSelector block."""
        super().__init__(
            title="Wait For Selector",
            block_type="wait",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("state", "attached")
        self.set_param("timeout", 30000)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait for selector action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            page = browser.current_page if browser else None
            if not page:
                raise Exception("No active page")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            state = self.get_param("state", "attached")
            timeout = self.get_param("timeout", 30000)

            logger.info(f"Waiting for selector: {selector}")

            await page.wait_for_selector(selector, state=state, timeout=timeout)

            self._executed = True
            self._result = {"success": True, "selector": selector}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"WaitForSelector block error: {e}")
            raise
