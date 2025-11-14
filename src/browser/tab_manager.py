"""
Tab manager for OctoMaster Pro.

Manages browser tabs/pages with switching and tracking.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from loguru import logger

from playwright.async_api import Page


@dataclass
class TabInfo:
    """Information about a browser tab."""

    page: Page
    index: int
    title: str
    url: str
    is_active: bool


class TabManager:
    """Manager for browser tabs/pages."""

    def __init__(self) -> None:
        """Initialize tab manager."""
        self._tabs: List[Page] = []
        self._active_index: int = -1

    @property
    def tabs(self) -> List[Page]:
        """Get all tabs.

        Returns:
            List of pages
        """
        return self._tabs

    @property
    def active_tab(self) -> Optional[Page]:
        """Get currently active tab.

        Returns:
            Active page or None
        """
        if 0 <= self._active_index < len(self._tabs):
            return self._tabs[self._active_index]
        return None

    @property
    def tab_count(self) -> int:
        """Get number of tabs.

        Returns:
            Tab count
        """
        return len(self._tabs)

    def add_tab(self, page: Page, make_active: bool = True) -> int:
        """Add new tab.

        Args:
            page: Page to add
            make_active: Whether to make this tab active

        Returns:
            Tab index
        """
        self._tabs.append(page)
        index = len(self._tabs) - 1

        if make_active:
            self._active_index = index

        logger.info(f"Tab added (index: {index}, total: {len(self._tabs)})")

        return index

    def remove_tab(self, index: int) -> bool:
        """Remove tab by index.

        Args:
            index: Tab index to remove

        Returns:
            True if removed successfully
        """
        if 0 <= index < len(self._tabs):
            self._tabs.pop(index)

            # Adjust active index
            if self._active_index == index:
                self._active_index = min(index, len(self._tabs) - 1)
            elif self._active_index > index:
                self._active_index -= 1

            logger.info(f"Tab removed (index: {index}, remaining: {len(self._tabs)})")
            return True

        return False

    def switch_to(self, index: int) -> Optional[Page]:
        """Switch to tab by index.

        Args:
            index: Tab index

        Returns:
            Page or None if invalid index
        """
        if 0 <= index < len(self._tabs):
            self._active_index = index
            logger.info(f"Switched to tab {index}")
            return self._tabs[index]

        return None

    def switch_next(self) -> Optional[Page]:
        """Switch to next tab (circular).

        Returns:
            Next page or None if no tabs
        """
        if not self._tabs:
            return None

        self._active_index = (self._active_index + 1) % len(self._tabs)
        return self.active_tab

    def switch_previous(self) -> Optional[Page]:
        """Switch to previous tab (circular).

        Returns:
            Previous page or None if no tabs
        """
        if not self._tabs:
            return None

        self._active_index = (self._active_index - 1) % len(self._tabs)
        return self.active_tab

    async def get_tab_info(self, index: int) -> Optional[TabInfo]:
        """Get information about tab.

        Args:
            index: Tab index

        Returns:
            Tab info or None if invalid index
        """
        if 0 <= index < len(self._tabs):
            page = self._tabs[index]

            try:
                title = await page.title()
                url = page.url
            except Exception:
                title = "Unknown"
                url = "about:blank"

            return TabInfo(
                page=page,
                index=index,
                title=title,
                url=url,
                is_active=(index == self._active_index),
            )

        return None

    async def get_all_tabs_info(self) -> List[TabInfo]:
        """Get information about all tabs.

        Returns:
            List of tab info
        """
        tabs_info = []

        for i in range(len(self._tabs)):
            info = await self.get_tab_info(i)
            if info:
                tabs_info.append(info)

        return tabs_info

    def find_tab_by_url(self, url: str) -> Optional[int]:
        """Find tab index by URL.

        Args:
            url: URL to search for

        Returns:
            Tab index or None if not found
        """
        for i, page in enumerate(self._tabs):
            if page.url == url:
                return i

        return None

    async def find_tab_by_title(self, title: str) -> Optional[int]:
        """Find tab index by title.

        Args:
            title: Title to search for

        Returns:
            Tab index or None if not found
        """
        for i, page in enumerate(self._tabs):
            try:
                page_title = await page.title()
                if title in page_title:
                    return i
            except Exception:
                continue

        return None

    def clear(self) -> None:
        """Clear all tabs."""
        self._tabs.clear()
        self._active_index = -1
        logger.info("All tabs cleared")
