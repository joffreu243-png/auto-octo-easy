"""
Anti-bot detection measures for scraping.
"""

import random
import asyncio
from typing import List, Optional
from loguru import logger


class AntiBotMeasures:
    """Make scraping look like human behavior."""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    ]

    VIEWPORTS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 1280, 'height': 720},
    ]

    def __init__(self, page: Any, context: Any = None) -> None:
        """Initialize anti-bot measures.

        Args:
            page: Playwright page
            context: Playwright context (optional)
        """
        self.page = page
        self.context = context

    async def enable_stealth(self) -> None:
        """Enable stealth mode."""
        try:
            await self._random_user_agent()
            await self._random_viewport()
            await self._inject_stealth_scripts()

            logger.info("Stealth mode enabled")

        except Exception as e:
            logger.error(f"Failed to enable stealth: {e}")

    async def _random_user_agent(self) -> None:
        """Set random user agent."""
        ua = random.choice(self.USER_AGENTS)
        await self.page.set_extra_http_headers({'User-Agent': ua})
        logger.debug(f"Set user agent: {ua[:50]}...")

    async def _random_viewport(self) -> None:
        """Set random viewport size."""
        viewport = random.choice(self.VIEWPORTS)
        await self.page.set_viewport_size(viewport)
        logger.debug(f"Set viewport: {viewport}")

    async def _inject_stealth_scripts(self) -> None:
        """Inject stealth JavaScript."""
        stealth_js = """
        // Overwrite the `plugins` property to use a custom getter.
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Overwrite the `languages` property to use a custom getter.
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Overwrite the `webdriver` property.
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // Remove automation indicators
        delete navigator.__proto__.webdriver;

        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """

        await self.page.add_init_script(stealth_js)
        logger.debug("Injected stealth scripts")

    async def human_like_delay(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """Add random human-like delay.

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)

    async def human_like_scroll(self) -> None:
        """Scroll like a human."""
        try:
            viewport_height = await self.page.evaluate("window.innerHeight")
            total_height = await self.page.evaluate("document.body.scrollHeight")

            current_position = 0

            while current_position < total_height:
                # Random scroll amount (1-3 viewport heights)
                scroll_amount = random.randint(int(viewport_height * 0.5), int(viewport_height * 2))

                # Scroll
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")

                # Random pause
                await self.human_like_delay(500, 2000)

                # Sometimes scroll back up a bit
                if random.random() < 0.2:
                    back_scroll = random.randint(50, 200)
                    await self.page.evaluate(f"window.scrollBy(0, -{back_scroll})")
                    await self.human_like_delay(200, 500)

                current_position += scroll_amount

            logger.debug("Human-like scroll completed")

        except Exception as e:
            logger.error(f"Human-like scroll failed: {e}")

    async def random_mouse_movement(self) -> None:
        """Simulate random mouse movements."""
        try:
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, 1920)
                y = random.randint(0, 1080)

                await self.page.mouse.move(x, y)
                await self.human_like_delay(50, 200)

        except Exception as e:
            logger.error(f"Mouse movement failed: {e}")

    async def solve_captcha(self, captcha_service: str = "2captcha", api_key: Optional[str] = None) -> bool:
        """Attempt to solve CAPTCHA.

        Args:
            captcha_service: CAPTCHA solving service
            api_key: API key for service

        Returns:
            True if solved
        """
        logger.warning("CAPTCHA solving not implemented")
        return False
