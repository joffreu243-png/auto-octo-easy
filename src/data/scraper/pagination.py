"""
Pagination handler for scraping multiple pages.
"""

from typing import Optional, Dict, Any, List
import asyncio
from loguru import logger

from src.data.types import PaginationType, PaginationConfig


class PaginationHandler:
    """Handle different types of pagination."""

    def __init__(self, page: Any) -> None:
        """Initialize pagination handler.

        Args:
            page: Playwright page
        """
        self.page = page

    async def detect_pagination(self) -> Optional[PaginationConfig]:
        """Auto-detect pagination on page.

        Returns:
            Pagination configuration or None
        """
        # Check for button pagination
        next_btn = await self._find_next_button()
        if next_btn:
            return PaginationConfig(
                type=PaginationType.BUTTON,
                selector=next_btn,
            )

        # Check for infinite scroll
        if await self._has_infinite_scroll():
            return PaginationConfig(
                type=PaginationType.INFINITE_SCROLL,
            )

        # Check for URL parameters
        url_param = await self._detect_url_param()
        if url_param:
            return PaginationConfig(
                type=PaginationType.URL_PARAM,
                param_name=url_param,
            )

        logger.info("No pagination detected")
        return None

    async def _find_next_button(self) -> Optional[str]:
        """Find "Next" button selector.

        Returns:
            Selector or None
        """
        selectors = [
            'a:has-text("Next")',
            'button:has-text("Next")',
            '.next',
            '.pagination-next',
            '[rel="next"]',
            'a:has-text("→")',
            'a:has-text("»")',
        ]

        for sel in selectors:
            try:
                element = await self.page.query_selector(sel)
                if element:
                    logger.debug(f"Found next button: {sel}")
                    return sel
            except:
                pass

        return None

    async def _has_infinite_scroll(self) -> bool:
        """Check if page has infinite scroll.

        Returns:
            True if infinite scroll detected
        """
        # Check if scrolling triggers new content
        initial_height = await self.page.evaluate("document.body.scrollHeight")

        # Scroll down
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        new_height = await self.page.evaluate("document.body.scrollHeight")

        return new_height > initial_height

    async def _detect_url_param(self) -> Optional[str]:
        """Detect URL pagination parameter.

        Returns:
            Parameter name or None
        """
        url = self.page.url
        common_params = ["page", "p", "pg", "offset", "start"]

        for param in common_params:
            if f"{param}=" in url:
                return param

        return None

    async def iterate_pages(
        self,
        config: Optional[PaginationConfig] = None,
        max_pages: int = 10,
        callback: Optional[callable] = None,
    ) -> List[Any]:
        """Iterate through all pages.

        Args:
            config: Pagination configuration
            max_pages: Maximum pages to scrape
            callback: Callback function for each page

        Returns:
            All collected data
        """
        if not config:
            config = await self.detect_pagination()

        if not config:
            logger.warning("No pagination detected, scraping single page")
            if callback:
                return [await callback(self.page)]
            return []

        all_data = []
        current_page = 1

        while current_page <= max_pages:
            logger.info(f"Scraping page {current_page}/{max_pages}")

            # Collect data from current page
            if callback:
                page_data = await callback(self.page)
                all_data.append(page_data)

            # Go to next page
            has_next = await self._go_next_page(config)
            if not has_next:
                logger.info("No more pages")
                break

            # Wait after loading
            await asyncio.sleep(config.wait_after_load)

            current_page += 1

        logger.info(f"Scraped {current_page} pages total")
        return all_data

    async def _go_next_page(self, config: PaginationConfig) -> bool:
        """Navigate to next page.

        Args:
            config: Pagination configuration

        Returns:
            True if navigation successful
        """
        try:
            if config.type == PaginationType.BUTTON:
                return await self._click_next_button(config.selector)

            elif config.type == PaginationType.INFINITE_SCROLL:
                return await self._scroll_to_load_more()

            elif config.type == PaginationType.URL_PARAM:
                return await self._next_url_param(config.param_name)

            return False

        except Exception as e:
            logger.error(f"Failed to go to next page: {e}")
            return False

    async def _click_next_button(self, selector: str) -> bool:
        """Click next button.

        Args:
            selector: Button selector

        Returns:
            True if successful
        """
        try:
            button = await self.page.query_selector(selector)
            if not button:
                return False

            # Check if button is disabled
            is_disabled = await button.is_disabled()
            if is_disabled:
                return False

            await button.click()
            await self.page.wait_for_load_state("networkidle")

            return True

        except Exception as e:
            logger.debug(f"Click next failed: {e}")
            return False

    async def _scroll_to_load_more(self) -> bool:
        """Scroll to trigger loading more content.

        Returns:
            True if more content loaded
        """
        try:
            old_height = await self.page.evaluate("document.body.scrollHeight")

            # Scroll to bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            new_height = await self.page.evaluate("document.body.scrollHeight")

            return new_height > old_height

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False

    async def _next_url_param(self, param_name: str) -> bool:
        """Navigate to next page via URL parameter.

        Args:
            param_name: Parameter name

        Returns:
            True if successful
        """
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

            current_url = self.page.url
            parsed = urlparse(current_url)
            params = parse_qs(parsed.query)

            # Get current page number
            current_page = int(params.get(param_name, [1])[0])
            next_page = current_page + 1

            # Update parameter
            params[param_name] = [str(next_page)]

            # Build new URL
            new_query = urlencode(params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            new_url = urlunparse(new_parsed)

            # Navigate
            await self.page.goto(new_url)
            await self.page.wait_for_load_state("networkidle")

            return True

        except Exception as e:
            logger.error(f"URL param navigation failed: {e}")
            return False
