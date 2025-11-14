"""
Browser automation using Playwright.
"""

from typing import Optional, Dict, Any
from loguru import logger


class Browser:
    """
    Browser automation wrapper.

    Provides a high-level API for browser automation using Playwright.
    """

    def __init__(self, browser_type: str = "chromium", headless: bool = False):
        """
        Initialize browser.

        Args:
            browser_type: Type of browser ('chromium', 'firefox', 'webkit')
            headless: Run in headless mode
        """
        self.browser_type = browser_type
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self, **kwargs):
        """Start the browser."""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()

            # Launch browser
            browser_launcher = getattr(self.playwright, self.browser_type)
            self.browser = await browser_launcher.launch(headless=self.headless, **kwargs)

            # Create context
            self.context = await self.browser.new_context()

            # Create page
            self.page = await self.context.new_page()

            logger.info(f"Browser started: {self.browser_type}")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    async def stop(self):
        """Stop the browser."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            logger.info("Browser stopped")

        except Exception as e:
            logger.error(f"Failed to stop browser: {e}")
            raise

    async def navigate(self, url: str, **kwargs):
        """Navigate to URL."""
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Navigating to: {url}")
        await self.page.goto(url, **kwargs)

    async def click(self, selector: str, **kwargs):
        """Click on element."""
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Clicking: {selector}")
        await self.page.click(selector, **kwargs)

    async def type_text(self, selector: str, text: str, **kwargs):
        """Type text into element."""
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Typing into {selector}: {text}")
        await self.page.fill(selector, text, **kwargs)

    async def get_text(self, selector: str) -> str:
        """Get text from element."""
        if not self.page:
            raise RuntimeError("Browser not started")

        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content()
        return ""

    async def screenshot(self, path: str, **kwargs):
        """Take screenshot."""
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Taking screenshot: {path}")
        await self.page.screenshot(path=path, **kwargs)

    async def wait_for_selector(self, selector: str, timeout: int = 30000):
        """Wait for element to appear."""
        if not self.page:
            raise RuntimeError("Browser not started")

        logger.info(f"Waiting for: {selector}")
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript expression."""
        if not self.page:
            raise RuntimeError("Browser not started")

        return await self.page.evaluate(expression)

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        import asyncio

        asyncio.run(self.stop())
