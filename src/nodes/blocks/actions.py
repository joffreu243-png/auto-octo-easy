"""
Action blocks for browser automation.

Blocks for user interactions: click, type, fill, select, etc.
"""

from typing import Dict, Any
from loguru import logger

from src.nodes.blocks.base import BaseBlock


class ClickBlock(BaseBlock):
    """Click element on page."""

    def __init__(self) -> None:
        """Initialize Click block."""
        super().__init__(
            title="Click Element",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("click_count", 1)
        self.set_param("button", "left")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute click action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            click_count = self.get_param("click_count", 1)

            logger.info(f"Clicking: {selector}")

            result = await browser.click(selector, click_count=click_count)

            if result.success:
                self._executed = True
                self._result = {"success": True, "selector": selector}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Click failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"Click block error: {e}")
            raise


class TypeTextBlock(BaseBlock):
    """Type text into element."""

    def __init__(self) -> None:
        """Initialize TypeText block."""
        super().__init__(
            title="Type Text",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("text", "")
        self.set_param("delay", 0)
        self.set_param("clear_first", False)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute type text action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            selector = self.get_param("selector")
            text = self.get_param("text")

            if not selector:
                raise Exception("Selector is required")

            delay = self.get_param("delay", 0)
            clear_first = self.get_param("clear_first", False)

            logger.info(f"Typing into: {selector}")

            result = await browser.type_text(
                selector, text, delay=delay, clear_first=clear_first
            )

            if result.success:
                self._executed = True
                self._result = {"success": True, "text": text}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Type failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"TypeText block error: {e}")
            raise


class FillBlock(BaseBlock):
    """Fill input field (faster than typing)."""

    def __init__(self) -> None:
        """Initialize Fill block."""
        super().__init__(
            title="Fill Field",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("value", "")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fill action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            selector = self.get_param("selector")
            value = self.get_param("value")

            if not selector:
                raise Exception("Selector is required")

            logger.info(f"Filling: {selector}")

            result = await browser.fill(selector, value)

            if result.success:
                self._executed = True
                self._result = {"success": True, "value": value}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Fill failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"Fill block error: {e}")
            raise


class SelectDropdownBlock(BaseBlock):
    """Select option from dropdown."""

    def __init__(self) -> None:
        """Initialize SelectDropdown block."""
        super().__init__(
            title="Select Dropdown",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("value", "")
        self.set_param("by", "value")  # value, label, or index

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute select action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions()
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            value = self.get_param("value")
            by = self.get_param("by", "value")

            if not selector:
                raise Exception("Selector is required")

            logger.info(f"Selecting from: {selector}")

            # Prepare kwargs based on selection method
            kwargs = {"selector": selector}
            if by == "value":
                kwargs["value"] = value
            elif by == "label":
                kwargs["label"] = value
            elif by == "index":
                kwargs["index"] = int(value)

            result = await actions.select_option(**kwargs)

            if result.success:
                self._executed = True
                self._result = {"success": True, "value": value}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Select failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"SelectDropdown block error: {e}")
            raise


class HoverBlock(BaseBlock):
    """Hover over element."""

    def __init__(self) -> None:
        """Initialize Hover block."""
        super().__init__(
            title="Hover Element",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hover action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions()
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            logger.info(f"Hovering: {selector}")

            result = await actions.hover(selector)

            if result.success:
                self._executed = True
                self._result = {"success": True}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Hover failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"Hover block error: {e}")
            raise


class ScrollBlock(BaseBlock):
    """Scroll page or element."""

    def __init__(self) -> None:
        """Initialize Scroll block."""
        super().__init__(
            title="Scroll",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")  # Empty = scroll page
        self.set_param("x", 0)
        self.set_param("y", 0)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scroll action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions()
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            x = self.get_param("x", 0)
            y = self.get_param("y", 0)

            logger.info(f"Scrolling")

            result = await actions.scroll_to(
                selector=selector if selector else None, x=x, y=y
            )

            if result.success:
                self._executed = True
                self._result = {"success": True}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Scroll failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"Scroll block error: {e}")
            raise


class ScreenshotBlock(BaseBlock):
    """Take screenshot of page."""

    def __init__(self) -> None:
        """Initialize Screenshot block."""
        super().__init__(
            title="Screenshot",
            block_type="action",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("path", "screenshot.png")
        self.set_param("full_page", False)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screenshot action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            if not browser:
                raise Exception("Browser not available")

            path = self.get_param("path", "screenshot.png")
            full_page = self.get_param("full_page", False)

            logger.info(f"Taking screenshot: {path}")

            result = await browser.screenshot(path=path, full_page=full_page)

            if result.success:
                self._executed = True
                self._result = {"success": True, "path": path}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Screenshot failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"Screenshot block error: {e}")
            raise
