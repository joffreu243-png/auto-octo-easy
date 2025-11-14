"""
Specialized table scraper.
"""

from typing import Dict, Any, List
from loguru import logger

from src.data.types import TableData
from datetime import datetime


class TableScraper:
    """Scrape HTML tables with advanced features."""

    def __init__(self, page: Any) -> None:
        """Initialize table scraper.

        Args:
            page: Playwright page
        """
        self.page = page

    async def scrape(self, selector: str = "table", has_header: bool = True) -> TableData:
        """Scrape table from page.

        Args:
            selector: Table CSS selector
            has_header: Whether table has header

        Returns:
            Table data
        """
        try:
            table = await self.page.query_selector(selector)
            if not table:
                return TableData(headers=[], rows=[], url=self.page.url)

            headers = await self._extract_headers(table) if has_header else []
            rows = await self._extract_rows(table, skip_first=has_header and not await table.query_selector("thead"))

            logger.info(f"Scraped table: {len(headers)} columns, {len(rows)} rows")

            return TableData(
                headers=headers,
                rows=rows,
                url=self.page.url,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Table scraping failed: {e}")
            return TableData(headers=[], rows=[], url=self.page.url)

    async def _extract_headers(self, table: Any) -> List[str]:
        """Extract table headers.

        Args:
            table: Table element

        Returns:
            List of header texts
        """
        headers = []

        # Try thead first
        header_cells = await table.query_selector_all("thead th, thead td")

        # Fallback to first row
        if not header_cells:
            first_row = await table.query_selector("tr:first-child")
            if first_row:
                header_cells = await first_row.query_selector_all("th, td")

        for cell in header_cells:
            text = await cell.inner_text()
            headers.append(text.strip())

        return headers

    async def _extract_rows(self, table: Any, skip_first: bool = False) -> List[List[str]]:
        """Extract table rows.

        Args:
            table: Table element
            skip_first: Skip first row (if it's header)

        Returns:
            List of rows
        """
        rows = []

        row_elements = await table.query_selector_all("tbody tr, tr")

        start_index = 1 if skip_first else 0

        for row_el in row_elements[start_index:]:
            cells = await row_el.query_selector_all("td, th")
            row_data = []

            for cell in cells:
                text = await cell.inner_text()
                row_data.append(text.strip())

            if row_data:
                rows.append(row_data)

        return rows

    async def scrape_all_tables(self) -> List[TableData]:
        """Scrape all tables on page.

        Returns:
            List of table data
        """
        tables = await self.page.query_selector_all("table")
        results = []

        for i, table in enumerate(tables):
            try:
                # Create unique selector for this table
                selector = f"table:nth-of-type({i + 1})"
                table_data = await self.scrape(selector)
                results.append(table_data)
            except:
                pass

        logger.info(f"Scraped {len(results)} tables")
        return results
