"""
Specialized list scraper.
"""

from typing import List, Dict, Any
from loguru import logger

from src.data.types import ListData
from datetime import datetime


class ListScraper:
    """Scrape lists (ul/ol) from pages."""

    def __init__(self, page: Any) -> None:
        """Initialize list scraper.

        Args:
            page: Playwright page
        """
        self.page = page

    async def scrape(self, selector: str = "ul, ol") -> ListData:
        """Scrape list from page.

        Args:
            selector: List CSS selector

        Returns:
            List data
        """
        try:
            list_element = await self.page.query_selector(selector)
            if not list_element:
                return ListData(items=[], url=self.page.url)

            items = await self._extract_items(list_element)

            logger.info(f"Scraped list: {len(items)} items")

            return ListData(
                items=items,
                url=self.page.url,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"List scraping failed: {e}")
            return ListData(items=[], url=self.page.url)

    async def _extract_items(self, list_element: Any) -> List[str]:
        """Extract list items.

        Args:
            list_element: List element

        Returns:
            List of item texts
        """
        items = []
        item_elements = await list_element.query_selector_all("li")

        for item in item_elements:
            text = await item.inner_text()
            items.append(text.strip())

        return items

    async def scrape_nested_list(self, selector: str = "ul, ol") -> Dict[str, Any]:
        """Scrape nested list structure.

        Args:
            selector: List CSS selector

        Returns:
            Nested list structure
        """
        list_element = await self.page.query_selector(selector)
        if not list_element:
            return {"items": []}

        return await self._extract_nested(list_element)

    async def _extract_nested(self, element: Any) -> Dict[str, Any]:
        """Extract nested list structure.

        Args:
            element: List element

        Returns:
            Nested structure
        """
        items = []
        item_elements = await element.query_selector_all(":scope > li")

        for item in item_elements:
            # Get text (excluding nested lists)
            text = await item.evaluate("el => el.childNodes[0]?.textContent || ''")

            # Check for nested list
            nested = await item.query_selector("ul, ol")

            if nested:
                items.append({
                    "text": text.strip(),
                    "children": await self._extract_nested(nested),
                })
            else:
                items.append(text.strip())

        return {"items": items}
