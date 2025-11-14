"""
Browser actions module for OctoMaster Pro.

Provides high-level browser actions: click, type, scroll, etc.
"""

from typing import Optional, Dict, Any, List, Union
from enum import Enum
from dataclasses import dataclass
import asyncio
from loguru import logger

from playwright.async_api import Page, ElementHandle, Locator


class MouseButton(Enum):
    """Mouse button types."""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyModifier(Enum):
    """Keyboard modifiers."""

    ALT = "Alt"
    CONTROL = "Control"
    META = "Meta"
    SHIFT = "Shift"


@dataclass
class ActionResult:
    """Result of browser action."""

    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None


class BrowserActions:
    """High-level browser actions using Playwright."""

    def __init__(self, page: Page) -> None:
        """Initialize browser actions.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self._default_timeout = 30000  # 30 seconds

    async def navigate(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Navigate to URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with navigation status
        """
        try:
            logger.info(f"Navigating to: {url}")
            await self.page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout or self._default_timeout,
            )
            return ActionResult(success=True, data={"url": url})
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def click(
        self,
        selector: str,
        button: MouseButton = MouseButton.LEFT,
        click_count: int = 1,
        delay: int = 0,
        modifiers: Optional[List[KeyModifier]] = None,
        timeout: Optional[int] = None,
        force: bool = False,
    ) -> ActionResult:
        """Click element.

        Args:
            selector: Element selector
            button: Mouse button to click
            click_count: Number of clicks
            delay: Delay between mousedown and mouseup (ms)
            modifiers: Keyboard modifiers
            timeout: Timeout in milliseconds
            force: Force click even if element is not visible

        Returns:
            ActionResult with click status
        """
        try:
            logger.info(f"Clicking: {selector}")

            mods = [m.value for m in modifiers] if modifiers else []

            await self.page.click(
                selector,
                button=button.value,
                click_count=click_count,
                delay=delay,
                modifiers=mods,
                timeout=timeout or self._default_timeout,
                force=force,
            )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def type_text(
        self,
        selector: str,
        text: str,
        delay: int = 0,
        timeout: Optional[int] = None,
        clear_first: bool = False,
    ) -> ActionResult:
        """Type text into element.

        Args:
            selector: Element selector
            text: Text to type
            delay: Delay between key presses (ms)
            timeout: Timeout in milliseconds
            clear_first: Clear existing text first

        Returns:
            ActionResult with typing status
        """
        try:
            logger.info(f"Typing into: {selector}")

            if clear_first:
                await self.page.fill(selector, "")

            await self.page.type(
                selector,
                text,
                delay=delay,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector, "text": text})
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def fill(
        self,
        selector: str,
        value: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Fill input field (faster than typing).

        Args:
            selector: Element selector
            value: Value to fill
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with fill status
        """
        try:
            logger.info(f"Filling: {selector}")

            await self.page.fill(
                selector,
                value,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector, "value": value})
        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def select_option(
        self,
        selector: str,
        value: Optional[Union[str, List[str]]] = None,
        label: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Select option(s) from dropdown.

        Args:
            selector: Select element selector
            value: Option value(s) to select
            label: Option label(s) to select
            index: Option index(es) to select
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with selection status
        """
        try:
            logger.info(f"Selecting option: {selector}")

            if value is not None:
                await self.page.select_option(
                    selector, value=value, timeout=timeout or self._default_timeout
                )
            elif label is not None:
                await self.page.select_option(
                    selector, label=label, timeout=timeout or self._default_timeout
                )
            elif index is not None:
                await self.page.select_option(
                    selector, index=index, timeout=timeout or self._default_timeout
                )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Select failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def check(
        self,
        selector: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Check checkbox or radio button.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with check status
        """
        try:
            logger.info(f"Checking: {selector}")

            await self.page.check(
                selector,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Check failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def uncheck(
        self,
        selector: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Uncheck checkbox.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with uncheck status
        """
        try:
            logger.info(f"Unchecking: {selector}")

            await self.page.uncheck(
                selector,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Uncheck failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def hover(
        self,
        selector: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Hover over element.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with hover status
        """
        try:
            logger.info(f"Hovering: {selector}")

            await self.page.hover(
                selector,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Hover failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def scroll_to(
        self,
        selector: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> ActionResult:
        """Scroll page or element.

        Args:
            selector: Element selector (if scrolling to element)
            x: Horizontal scroll position
            y: Vertical scroll position

        Returns:
            ActionResult with scroll status
        """
        try:
            if selector:
                logger.info(f"Scrolling to element: {selector}")
                await self.page.locator(selector).scroll_into_view_if_needed()
            elif x is not None or y is not None:
                logger.info(f"Scrolling to position: ({x}, {y})")
                await self.page.evaluate(f"window.scrollTo({x or 0}, {y or 0})")

            return ActionResult(success=True)
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def press_key(
        self,
        key: str,
        delay: int = 0,
    ) -> ActionResult:
        """Press keyboard key.

        Args:
            key: Key to press (e.g., 'Enter', 'ArrowDown')
            delay: Delay between keydown and keyup (ms)

        Returns:
            ActionResult with key press status
        """
        try:
            logger.info(f"Pressing key: {key}")

            await self.page.keyboard.press(key, delay=delay)

            return ActionResult(success=True, data={"key": key})
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> ActionResult:
        """Take screenshot.

        Args:
            path: File path to save screenshot
            full_page: Capture full scrollable page
            selector: Element selector for element screenshot

        Returns:
            ActionResult with screenshot data
        """
        try:
            logger.info("Taking screenshot")

            if selector:
                element = await self.page.locator(selector)
                screenshot_bytes = await element.screenshot()
            else:
                screenshot_bytes = await self.page.screenshot(
                    path=path, full_page=full_page
                )

            return ActionResult(
                success=True,
                data={"path": path, "bytes": screenshot_bytes},
            )
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Wait for element to match state.

        Args:
            selector: Element selector
            state: Element state (visible, attached, detached, hidden)
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with wait status
        """
        try:
            logger.info(f"Waiting for selector: {selector} (state: {state})")

            await self.page.wait_for_selector(
                selector,
                state=state,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            logger.error(f"Wait for selector failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def get_text(
        self,
        selector: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Get element text content.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with text content
        """
        try:
            logger.info(f"Getting text from: {selector}")

            text = await self.page.text_content(
                selector,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"text": text})
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def get_attribute(
        self,
        selector: str,
        attribute: str,
        timeout: Optional[int] = None,
    ) -> ActionResult:
        """Get element attribute value.

        Args:
            selector: Element selector
            attribute: Attribute name
            timeout: Timeout in milliseconds

        Returns:
            ActionResult with attribute value
        """
        try:
            logger.info(f"Getting attribute '{attribute}' from: {selector}")

            value = await self.page.get_attribute(
                selector,
                attribute,
                timeout=timeout or self._default_timeout,
            )

            return ActionResult(success=True, data={"value": value})
        except Exception as e:
            logger.error(f"Get attribute failed: {e}")
            return ActionResult(success=False, error=str(e))

    async def evaluate(
        self,
        expression: str,
        arg: Optional[Any] = None,
    ) -> ActionResult:
        """Evaluate JavaScript expression.

        Args:
            expression: JavaScript expression
            arg: Optional argument to pass to expression

        Returns:
            ActionResult with evaluation result
        """
        try:
            logger.info("Evaluating JavaScript")

            result = await self.page.evaluate(expression, arg)

            return ActionResult(success=True, data={"result": result})
        except Exception as e:
            logger.error(f"Evaluate failed: {e}")
            return ActionResult(success=False, error=str(e))
