"""
Browser controller for OctoMaster Pro.

Main browser controller integrating all browser components.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
from loguru import logger

from playwright.async_api import Page

from src.browser.playwright_bridge import PlaywrightBridge
from src.browser.actions import BrowserActions, ActionResult
from src.browser.selector_engine import SelectorEngine
from src.browser.cdp_client import CDPClient
from src.browser.tab_manager import TabManager, TabInfo
from src.browser.inspector import ElementInspector, ElementInfo
from src.core.exceptions import BrowserError


class BrowserController:
    """Main browser controller integrating all browser components."""

    def __init__(self) -> None:
        """Initialize browser controller."""
        self.playwright = PlaywrightBridge()
        self.tab_manager = TabManager()
        self._actions: Optional[BrowserActions] = None
        self._selector_engine: Optional[SelectorEngine] = None
        self._cdp_client: Optional[CDPClient] = None
        self._inspector: Optional[ElementInspector] = None

    @property
    def is_running(self) -> bool:
        """Check if browser is running.

        Returns:
            True if browser is running
        """
        return self.playwright.is_running

    @property
    def current_page(self) -> Optional[Page]:
        """Get current active page.

        Returns:
            Current page or None
        """
        return self.tab_manager.active_tab

    async def start(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        user_data_dir: Optional[Path] = None,
        args: Optional[List[str]] = None,
    ) -> bool:
        """Start browser.

        Args:
            browser_type: Browser type (chromium, firefox, webkit)
            headless: Run in headless mode
            user_data_dir: User data directory for persistent context
            args: Additional browser arguments

        Returns:
            True if started successfully

        Raises:
            BrowserError: If browser fails to start
        """
        try:
            logger.info(f"Starting browser ({browser_type})")

            # Start Playwright
            success = await self.playwright.start(
                browser_type=browser_type,
                headless=headless,
                user_data_dir=user_data_dir,
                args=args,
            )

            if not success:
                raise BrowserError("Failed to start browser")

            # Get initial page
            page = self.playwright.current_page
            if page:
                self.tab_manager.add_tab(page)
                await self._initialize_page_components(page)

            logger.info("Browser started successfully")
            return True

        except Exception as e:
            logger.error(f"Browser start failed: {e}")
            raise BrowserError(f"Failed to start browser: {e}")

    async def stop(self) -> None:
        """Stop browser and cleanup resources."""
        try:
            logger.info("Stopping browser")

            # Cleanup components
            if self._cdp_client:
                await self._cdp_client.disconnect()

            # Close all tabs
            for page in self.tab_manager.tabs:
                try:
                    await page.close()
                except Exception:
                    pass

            # Stop Playwright
            await self.playwright.stop()

            # Clear managers
            self.tab_manager.clear()
            self._actions = None
            self._selector_engine = None
            self._cdp_client = None
            self._inspector = None

            logger.info("Browser stopped")

        except Exception as e:
            logger.error(f"Browser stop error: {e}")

    async def _initialize_page_components(self, page: Page) -> None:
        """Initialize page-specific components.

        Args:
            page: Page to initialize components for
        """
        self._actions = BrowserActions(page)
        self._selector_engine = SelectorEngine(page)
        self._inspector = ElementInspector(page)
        self._cdp_client = CDPClient(page)

    # Navigation methods
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> ActionResult:
        """Navigate to URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete

        Returns:
            ActionResult with navigation status
        """
        if not self._actions:
            raise BrowserError("Browser not started")

        return await self._actions.navigate(url, wait_until)

    async def go_back(self) -> None:
        """Navigate back in history."""
        page = self.current_page
        if page:
            await page.go_back()

    async def go_forward(self) -> None:
        """Navigate forward in history."""
        page = self.current_page
        if page:
            await page.go_forward()

    async def reload(self) -> None:
        """Reload current page."""
        page = self.current_page
        if page:
            await page.reload()

    # Action methods
    async def click(self, selector: str, **kwargs) -> ActionResult:
        """Click element.

        Args:
            selector: Element selector
            **kwargs: Additional click options

        Returns:
            ActionResult with click status
        """
        if not self._actions:
            raise BrowserError("Browser not started")

        return await self._actions.click(selector, **kwargs)

    async def type_text(self, selector: str, text: str, **kwargs) -> ActionResult:
        """Type text into element.

        Args:
            selector: Element selector
            text: Text to type
            **kwargs: Additional typing options

        Returns:
            ActionResult with typing status
        """
        if not self._actions:
            raise BrowserError("Browser not started")

        return await self._actions.type_text(selector, text, **kwargs)

    async def fill(self, selector: str, value: str) -> ActionResult:
        """Fill input field.

        Args:
            selector: Element selector
            value: Value to fill

        Returns:
            ActionResult with fill status
        """
        if not self._actions:
            raise BrowserError("Browser not started")

        return await self._actions.fill(selector, value)

    async def screenshot(
        self, path: Optional[str] = None, full_page: bool = False
    ) -> ActionResult:
        """Take screenshot.

        Args:
            path: File path to save screenshot
            full_page: Capture full scrollable page

        Returns:
            ActionResult with screenshot data
        """
        if not self._actions:
            raise BrowserError("Browser not started")

        return await self._actions.screenshot(path, full_page)

    # Tab management
    async def new_tab(self) -> Page:
        """Create new tab.

        Returns:
            New page instance
        """
        page = await self.playwright.new_page()
        self.tab_manager.add_tab(page)
        await self._initialize_page_components(page)
        return page

    async def close_tab(self, index: Optional[int] = None) -> None:
        """Close tab.

        Args:
            index: Tab index (current tab if None)
        """
        if index is None:
            page = self.current_page
            if page:
                await self.playwright.close_page(page)
                tab_index = self.tab_manager.tabs.index(page)
                self.tab_manager.remove_tab(tab_index)
        else:
            if 0 <= index < self.tab_manager.tab_count:
                page = self.tab_manager.tabs[index]
                await self.playwright.close_page(page)
                self.tab_manager.remove_tab(index)

    async def switch_tab(self, index: int) -> Optional[Page]:
        """Switch to tab by index.

        Args:
            index: Tab index

        Returns:
            Page or None if invalid index
        """
        page = self.tab_manager.switch_to(index)
        if page:
            await self._initialize_page_components(page)
        return page

    async def get_tabs_info(self) -> List[TabInfo]:
        """Get information about all tabs.

        Returns:
            List of tab info
        """
        return await self.tab_manager.get_all_tabs_info()

    # Element inspection
    async def inspect_element(self, selector: str) -> Optional[ElementInfo]:
        """Inspect element and get detailed information.

        Args:
            selector: Element selector

        Returns:
            Element info or None if not found
        """
        if not self._inspector:
            raise BrowserError("Browser not started")

        return await self._inspector.inspect_element(selector)

    async def highlight_element(
        self, selector: str, color: str = "#ff0000", duration: Optional[int] = None
    ) -> bool:
        """Highlight element on page.

        Args:
            selector: Element selector
            color: Highlight color
            duration: Highlight duration in ms (None = permanent)

        Returns:
            True if highlighted successfully
        """
        if not self._inspector:
            raise BrowserError("Browser not started")

        return await self._inspector.highlight_element(selector, color, duration)

    # Advanced features
    async def enable_cdp(self) -> bool:
        """Enable Chrome DevTools Protocol.

        Returns:
            True if enabled successfully
        """
        if not self._cdp_client:
            raise BrowserError("Browser not started")

        return await self._cdp_client.connect()

    async def execute_cdp_command(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute CDP command.

        Args:
            method: CDP method name
            params: Method parameters

        Returns:
            Command result
        """
        if not self._cdp_client:
            raise BrowserError("Browser not started")

        return await self._cdp_client.send(method, params)

    async def emulate_device(self, device_name: str) -> None:
        """Emulate mobile device.

        Args:
            device_name: Device name (e.g., 'iPhone 12')
        """
        await self.playwright.emulate_device(device_name)

    def get_actions(self) -> Optional[BrowserActions]:
        """Get browser actions instance.

        Returns:
            BrowserActions or None
        """
        return self._actions

    def get_selector_engine(self) -> Optional[SelectorEngine]:
        """Get selector engine instance.

        Returns:
            SelectorEngine or None
        """
        return self._selector_engine
