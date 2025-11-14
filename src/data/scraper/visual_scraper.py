"""
Visual web scraper with automatic structure detection.
"""

from typing import Dict, Any, List, Optional
from loguru import logger


class VisualScraper:
    """Visual scraper that detects and extracts structured data automatically."""

    def __init__(self, page: Any) -> None:
        """Initialize visual scraper.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.selected_elements = []

    async def detect_structure(self, selector: str) -> Dict[str, Any]:
        """Detect structure of selected area.

        Args:
            selector: CSS selector for area

        Returns:
            Structure info with type and data
        """
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return {"type": "none", "data": []}

            # Detect type
            structure_type = await self._detect_type(element)

            if structure_type == "table":
                return await self._extract_table(element)
            elif structure_type == "list":
                return await self._extract_list(element)
            elif structure_type == "cards":
                return await self._extract_cards(element)
            else:
                return {"type": "single", "data": [await element.inner_text()]}

        except Exception as e:
            logger.error(f"Structure detection failed: {e}")
            return {"type": "error", "data": []}

    async def _detect_type(self, element: Any) -> str:
        """Detect structure type.

        Args:
            element: Element to analyze

        Returns:
            Structure type
        """
        # Check for table
        if await element.query_selector("table"):
            return "table"

        # Check for list
        if await element.query_selector("ul") or await element.query_selector("ol"):
            return "list"

        # Check for repeating children (cards/grid)
        children = await element.query_selector_all(":scope > *")
        if len(children) > 3:
            return "cards"

        return "single"

    async def _extract_table(self, element: Any) -> Dict[str, Any]:
        """Extract data from table.

        Args:
            element: Table element

        Returns:
            Table data
        """
        table = await element.query_selector("table") or element

        # Get headers
        headers = []
        header_cells = await table.query_selector_all("thead th, tr:first-child th")
        for cell in header_cells:
            headers.append(await cell.inner_text())

        # Get rows
        rows = []
        row_elements = await table.query_selector_all("tbody tr, tr")

        for row_el in row_elements[1 if headers else 0:]:
            cells = await row_el.query_selector_all("td, th")
            row_data = [await cell.inner_text() for cell in cells]
            if row_data:
                rows.append(row_data)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    async def _extract_list(self, element: Any) -> Dict[str, Any]:
        """Extract data from list.

        Args:
            element: List element

        Returns:
            List data
        """
        list_el = await element.query_selector("ul, ol") or element
        items = await list_el.query_selector_all("li")

        data = [await item.inner_text() for item in items]

        return {
            "type": "list",
            "data": data,
        }

    async def _extract_cards(self, element: Any) -> Dict[str, Any]:
        """Extract data from card-like structures.

        Args:
            element: Container element

        Returns:
            Cards data
        """
        children = await element.query_selector_all(":scope > *")

        # Sample first few to detect pattern
        pattern = await self._detect_pattern(children[:min(5, len(children))])

        # Extract using pattern
        data = []
        for child in children:
            item = await self._extract_by_pattern(child, pattern)
            if item:
                data.append(item)

        return {
            "type": "cards",
            "pattern": pattern,
            "data": data,
        }

    async def _detect_pattern(self, samples: List[Any]) -> Dict[str, str]:
        """Detect common pattern in elements.

        Args:
            samples: Sample elements

        Returns:
            Pattern dictionary
        """
        pattern = {}

        if not samples:
            return pattern

        # Check for common child selectors
        first = samples[0]

        # Title/heading
        if await first.query_selector("h1, h2, h3, h4, .title, .heading"):
            pattern["title"] = "h1, h2, h3, h4, .title, .heading"

        # Description/text
        if await first.query_selector("p, .description, .text"):
            pattern["description"] = "p, .description, .text"

        # Image
        if await first.query_selector("img"):
            pattern["image"] = "img"

        # Link
        if await first.query_selector("a"):
            pattern["link"] = "a"

        return pattern

    async def _extract_by_pattern(self, element: Any, pattern: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data using pattern.

        Args:
            element: Element to extract from
            pattern: Pattern dictionary

        Returns:
            Extracted data
        """
        data = {}

        for key, selector in pattern.items():
            try:
                el = await element.query_selector(selector)
                if el:
                    if key == "image":
                        data[key] = await el.get_attribute("src")
                    elif key == "link":
                        data[key] = await el.get_attribute("href")
                    else:
                        data[key] = await el.inner_text()
            except:
                pass

        return data if data else None
