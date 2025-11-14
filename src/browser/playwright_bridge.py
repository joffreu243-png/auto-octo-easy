"""
Playwright bridge for OctoMaster Pro.

Provides async wrapper over Playwright with event handling and page management.
"""

from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
import asyncio
from loguru import logger

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
    Error as PlaywrightError,
)


class PlaywrightBridge:
    """Async bridge to Playwright."""

    def __init__(self) -> None:
        """Initialize Playwright bridge."""
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._pages: List[Page] = []
        self._current_page: Optional[Page] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Check if browser is running.

        Returns:
            True if browser is running
        """
        return self._is_running

    @property
    def current_page(self) -> Optional[Page]:
        """Get current active page.

        Returns:
            Current page or None
        """
        return self._current_page

    @property
    def pages(self) -> List[Page]:
        """Get all pages.

        Returns:
            List of pages
        """
        return self._pages

    async def start(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        args: Optional[List[str]] = None,
        user_data_dir: Optional[Path] = None,
    ) -> bool:
        """Start Playwright and launch browser.

        Args:
            browser_type: Browser type (chromium, firefox, webkit)
            headless: Run in headless mode
            args: Additional browser arguments
            user_data_dir: User data directory for persistent context

        Returns:
            True if started successfully
        """
        try:
            logger.info(f"Starting Playwright ({browser_type}, headless={headless})")

            # Start Playwright
            self._playwright = await async_playwright().start()

            # Get browser type
            if browser_type == "chromium":
                browser_launcher = self._playwright.chromium
            elif browser_type == "firefox":
                browser_launcher = self._playwright.firefox
            elif browser_type == "webkit":
                browser_launcher = self._playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            # Launch browser
            launch_options = {
                "headless": headless,
                "args": args or [],
            }

            if user_data_dir:
                # Launch persistent context
                self._context = await browser_launcher.launch_persistent_context(
                    str(user_data_dir),
                    **launch_options,
                )
                self._browser = None  # No browser object in persistent mode
            else:
                # Launch browser
                self._browser = await browser_launcher.launch(**launch_options)
                self._context = await self._browser.new_context()

            # Create initial page
            page = await self._context.new_page()
            self._pages.append(page)
            self._current_page = page

            # Setup event listeners
            self._setup_page_events(page)

            self._is_running = True
            logger.info("Playwright started successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            await self.stop()
            return False

    async def stop(self) -> None:
        """Stop Playwright and close browser."""
        try:
            logger.info("Stopping Playwright")

            # Close all pages
            for page in self._pages:
                try:
                    await page.close()
                except Exception:
                    pass

            # Close context
            if self._context:
                try:
                    await self._context.close()
                except Exception:
                    pass

            # Close browser
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass

            # Stop Playwright
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass

            self._playwright = None
            self._browser = None
            self._context = None
            self._pages = []
            self._current_page = None
            self._is_running = False

            logger.info("Playwright stopped")

        except Exception as e:
            logger.error(f"Error stopping Playwright: {e}")

    async def new_page(self) -> Page:
        """Create new page/tab.

        Returns:
            New page instance
        """
        if not self._context:
            raise RuntimeError("Browser not started")

        page = await self._context.new_page()
        self._pages.append(page)
        self._current_page = page

        # Setup event listeners
        self._setup_page_events(page)

        logger.info(f"New page created (total: {len(self._pages)})")

        return page

    async def close_page(self, page: Page) -> None:
        """Close specific page.

        Args:
            page: Page to close
        """
        try:
            await page.close()
            if page in self._pages:
                self._pages.remove(page)

            # Set current page to last page if available
            if self._current_page == page:
                self._current_page = self._pages[-1] if self._pages else None

            logger.info(f"Page closed (remaining: {len(self._pages)})")

        except Exception as e:
            logger.error(f"Error closing page: {e}")

    async def switch_page(self, index: int) -> Optional[Page]:
        """Switch to page by index.

        Args:
            index: Page index

        Returns:
            Page or None if index invalid
        """
        if 0 <= index < len(self._pages):
            self._current_page = self._pages[index]
            logger.info(f"Switched to page {index}")
            return self._current_page

        return None

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        page: Optional[Page] = None,
    ) -> bytes:
        """Take screenshot of page.

        Args:
            path: File path to save screenshot
            full_page: Capture full scrollable page
            page: Page to screenshot (current if None)

        Returns:
            Screenshot bytes
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        screenshot_bytes = await target_page.screenshot(
            path=path,
            full_page=full_page,
        )

        logger.info(f"Screenshot captured (full_page={full_page})")

        return screenshot_bytes

    async def pdf(
        self,
        path: str,
        page: Optional[Page] = None,
    ) -> None:
        """Generate PDF of page.

        Args:
            path: File path to save PDF
            page: Page to export (current if None)
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        await target_page.pdf(path=path)

        logger.info(f"PDF saved to: {path}")

    async def set_viewport(
        self,
        width: int,
        height: int,
        page: Optional[Page] = None,
    ) -> None:
        """Set viewport size.

        Args:
            width: Viewport width
            height: Viewport height
            page: Page to resize (current if None)
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        await target_page.set_viewport_size({"width": width, "height": height})

        logger.info(f"Viewport set to {width}x{height}")

    async def emulate_device(
        self,
        device_name: str,
        page: Optional[Page] = None,
    ) -> None:
        """Emulate mobile device.

        Args:
            device_name: Device name (e.g., 'iPhone 12')
            page: Page to emulate (current if None)
        """
        if not self._playwright:
            raise RuntimeError("Playwright not started")

        # Get device descriptor
        devices = self._playwright.devices
        if device_name not in devices:
            raise ValueError(f"Unknown device: {device_name}")

        device = devices[device_name]
        target_page = page or self._current_page

        if not target_page:
            raise RuntimeError("No active page")

        # Apply device settings
        await target_page.set_viewport_size(device["viewport"])
        await target_page.emulate_media(
            media=device.get("defaultBrowserType", "screen")
        )

        logger.info(f"Emulating device: {device_name}")

    async def intercept_requests(
        self,
        callback: Callable,
        page: Optional[Page] = None,
    ) -> None:
        """Intercept network requests.

        Args:
            callback: Callback function for requests
            page: Page to intercept (current if None)
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        await target_page.route("**/*", callback)

        logger.info("Request interception enabled")

    async def block_resources(
        self,
        resource_types: List[str],
        page: Optional[Page] = None,
    ) -> None:
        """Block specific resource types.

        Args:
            resource_types: List of resource types to block
                           (image, stylesheet, font, script, etc.)
            page: Page to configure (current if None)
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        async def route_handler(route, request):
            if request.resource_type in resource_types:
                await route.abort()
            else:
                await route.continue_()

        await target_page.route("**/*", route_handler)

        logger.info(f"Blocking resources: {resource_types}")

    async def evaluate_script(
        self,
        script: str,
        arg: Optional[Any] = None,
        page: Optional[Page] = None,
    ) -> Any:
        """Evaluate JavaScript in page context.

        Args:
            script: JavaScript code to evaluate
            arg: Optional argument to pass
            page: Page to evaluate in (current if None)

        Returns:
            Evaluation result
        """
        target_page = page or self._current_page
        if not target_page:
            raise RuntimeError("No active page")

        result = await target_page.evaluate(script, arg)

        return result

    def on(self, event: str, handler: Callable) -> None:
        """Register event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []

        self._event_handlers[event].append(handler)

    def _setup_page_events(self, page: Page) -> None:
        """Setup event listeners for page.

        Args:
            page: Page to setup events for
        """
        # Console events
        page.on("console", lambda msg: self._emit("console", msg))

        # Dialog events
        page.on("dialog", lambda dialog: self._emit("dialog", dialog))

        # Request events
        page.on("request", lambda request: self._emit("request", request))
        page.on("response", lambda response: self._emit("response", response))

        # Navigation events
        page.on("load", lambda: self._emit("load", page))
        page.on(
            "domcontentloaded", lambda: self._emit("domcontentloaded", page)
        )

        # Error events
        page.on("pageerror", lambda error: self._emit("pageerror", error))
        page.on("crash", lambda: self._emit("crash", page))

    def _emit(self, event: str, *args) -> None:
        """Emit event to handlers.

        Args:
            event: Event name
            *args: Event arguments
        """
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args)
                except Exception as e:
                    logger.error(f"Event handler error ({event}): {e}")
