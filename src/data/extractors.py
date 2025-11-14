"""
Data extractors for OctoMaster Pro.

Provides various extractors for different data types from web pages.
"""

from typing import List, Optional, Any, Dict
from loguru import logger


class BaseExtractor:
    """Base class for all extractors."""

    def __init__(self, selector: str, clean: bool = True) -> None:
        """Initialize extractor.

        Args:
            selector: CSS selector for elements
            clean: Whether to clean extracted data
        """
        self.selector = selector
        self.clean = clean

    async def extract(self, page: Any) -> List[Any]:
        """Extract data from page.

        Args:
            page: Playwright page instance

        Returns:
            Extracted data
        """
        raise NotImplementedError


class TextExtractor(BaseExtractor):
    """Extract text content from elements."""

    async def extract(self, page: Any) -> List[str]:
        """Extract text from page.

        Args:
            page: Playwright page

        Returns:
            List of text content
        """
        try:
            elements = await page.query_selector_all(self.selector)
            texts = []

            for element in elements:
                text = await element.inner_text()
                if self.clean:
                    text = self._clean_text(text)
                texts.append(text)

            logger.debug(f"Extracted {len(texts)} text items")
            return texts

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean extracted text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        import re

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        return text


class AttributeExtractor(BaseExtractor):
    """Extract element attributes."""

    def __init__(self, selector: str, attribute: str, clean: bool = True) -> None:
        """Initialize attribute extractor.

        Args:
            selector: CSS selector
            attribute: Attribute name to extract
            clean: Whether to clean data
        """
        super().__init__(selector, clean)
        self.attribute = attribute

    async def extract(self, page: Any) -> List[str]:
        """Extract attributes from elements.

        Args:
            page: Playwright page

        Returns:
            List of attribute values
        """
        try:
            elements = await page.query_selector_all(self.selector)
            attributes = []

            for element in elements:
                attr = await element.get_attribute(self.attribute)
                if attr:
                    if self.clean:
                        attr = attr.strip()
                    attributes.append(attr)

            logger.debug(f"Extracted {len(attributes)} {self.attribute} attributes")
            return attributes

        except Exception as e:
            logger.error(f"Attribute extraction failed: {e}")
            return []


class LinkExtractor(AttributeExtractor):
    """Extract links (href attributes)."""

    def __init__(self, selector: str = "a", absolute: bool = True) -> None:
        """Initialize link extractor.

        Args:
            selector: CSS selector for links
            absolute: Convert to absolute URLs
        """
        super().__init__(selector, "href")
        self.absolute = absolute

    async def extract(self, page: Any) -> List[str]:
        """Extract links from page.

        Args:
            page: Playwright page

        Returns:
            List of URLs
        """
        links = await super().extract(page)

        if self.absolute:
            base_url = page.url
            links = [self._make_absolute(link, base_url) for link in links]

        return links

    def _make_absolute(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute.

        Args:
            url: Relative or absolute URL
            base_url: Base URL

        Returns:
            Absolute URL
        """
        from urllib.parse import urljoin
        return urljoin(base_url, url)


class ImageExtractor(AttributeExtractor):
    """Extract image URLs (src attributes)."""

    def __init__(self, selector: str = "img", absolute: bool = True) -> None:
        """Initialize image extractor.

        Args:
            selector: CSS selector for images
            absolute: Convert to absolute URLs
        """
        super().__init__(selector, "src")
        self.absolute = absolute

    async def extract(self, page: Any) -> List[str]:
        """Extract image URLs from page.

        Args:
            page: Playwright page

        Returns:
            List of image URLs
        """
        images = await super().extract(page)

        if self.absolute:
            base_url = page.url
            from urllib.parse import urljoin
            images = [urljoin(base_url, img) for img in images]

        return images


class HTMLExtractor(BaseExtractor):
    """Extract HTML content."""

    async def extract(self, page: Any) -> List[str]:
        """Extract HTML from elements.

        Args:
            page: Playwright page

        Returns:
            List of HTML strings
        """
        try:
            elements = await page.query_selector_all(self.selector)
            html_list = []

            for element in elements:
                html = await element.inner_html()
                html_list.append(html)

            logger.debug(f"Extracted {len(html_list)} HTML blocks")
            return html_list

        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            return []


class TableExtractor(BaseExtractor):
    """Extract data from tables."""

    def __init__(self, selector: str = "table", has_header: bool = True) -> None:
        """Initialize table extractor.

        Args:
            selector: CSS selector for table
            has_header: Whether table has header row
        """
        super().__init__(selector)
        self.has_header = has_header

    async def extract(self, page: Any) -> Dict[str, Any]:
        """Extract table data.

        Args:
            page: Playwright page

        Returns:
            Dictionary with headers and rows
        """
        try:
            table = await page.query_selector(self.selector)
            if not table:
                return {"headers": [], "rows": []}

            # Extract headers
            headers = []
            if self.has_header:
                header_cells = await table.query_selector_all("thead th, tr:first-child th")
                for cell in header_cells:
                    text = await cell.inner_text()
                    headers.append(text.strip())

            # Extract rows
            rows = []
            row_elements = await table.query_selector_all("tbody tr, tr")

            start_index = 1 if self.has_header and not await table.query_selector("thead") else 0

            for row_el in row_elements[start_index:]:
                cells = await row_el.query_selector_all("td, th")
                row_data = []
                for cell in cells:
                    text = await cell.inner_text()
                    row_data.append(text.strip())
                if row_data:
                    rows.append(row_data)

            logger.debug(f"Extracted table: {len(headers)} columns, {len(rows)} rows")

            return {
                "headers": headers,
                "rows": rows,
            }

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return {"headers": [], "rows": []}


class ListExtractor(BaseExtractor):
    """Extract data from lists (ul/ol)."""

    def __init__(self, selector: str = "ul, ol") -> None:
        """Initialize list extractor.

        Args:
            selector: CSS selector for list
        """
        super().__init__(selector)

    async def extract(self, page: Any) -> List[str]:
        """Extract list items.

        Args:
            page: Playwright page

        Returns:
            List of item texts
        """
        try:
            list_element = await page.query_selector(self.selector)
            if not list_element:
                return []

            items = await list_element.query_selector_all("li")
            item_texts = []

            for item in items:
                text = await item.inner_text()
                if self.clean:
                    text = text.strip()
                item_texts.append(text)

            logger.debug(f"Extracted {len(item_texts)} list items")
            return item_texts

        except Exception as e:
            logger.error(f"List extraction failed: {e}")
            return []


class MetaExtractor:
    """Extract meta tags from page."""

    async def extract(self, page: Any) -> Dict[str, str]:
        """Extract meta tags.

        Args:
            page: Playwright page

        Returns:
            Dictionary of meta tags
        """
        try:
            meta_tags = {}

            # Get all meta tags
            metas = await page.query_selector_all("meta")

            for meta in metas:
                name = await meta.get_attribute("name") or await meta.get_attribute("property")
                content = await meta.get_attribute("content")

                if name and content:
                    meta_tags[name] = content

            logger.debug(f"Extracted {len(meta_tags)} meta tags")
            return meta_tags

        except Exception as e:
            logger.error(f"Meta extraction failed: {e}")
            return {}
