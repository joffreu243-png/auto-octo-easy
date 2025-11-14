"""
Selector engine for OctoMaster Pro.

Provides intelligent element selection with multiple strategies and fallbacks.
"""

from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from playwright.async_api import Page, ElementHandle


class SelectorStrategy(Enum):
    """Selector strategy types."""

    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ID = "id"
    NAME = "name"
    CLASS = "class"
    TAG = "tag"
    ARIA = "aria"
    ROLE = "role"
    TEST_ID = "test-id"


@dataclass
class SelectorInfo:
    """Information about a selector."""

    selector: str
    strategy: SelectorStrategy
    score: float  # Selector quality score (0-100)
    unique: bool  # Whether selector matches single element
    stable: bool  # Whether selector is likely stable


class SelectorEngine:
    """Intelligent selector engine with multiple strategies."""

    def __init__(self, page: Page) -> None:
        """Initialize selector engine.

        Args:
            page: Playwright page instance
        """
        self.page = page

    async def find_element(
        self,
        selector: str,
        strategy: Optional[SelectorStrategy] = None,
    ) -> Optional[ElementHandle]:
        """Find element using selector.

        Args:
            selector: Element selector
            strategy: Selector strategy (auto-detect if None)

        Returns:
            Element handle or None if not found
        """
        try:
            if strategy == SelectorStrategy.XPATH:
                return await self.page.query_selector(f"xpath={selector}")
            elif strategy == SelectorStrategy.TEXT:
                return await self.page.query_selector(f"text={selector}")
            elif strategy == SelectorStrategy.ROLE:
                return await self.page.query_selector(f"role={selector}")
            else:
                return await self.page.query_selector(selector)
        except Exception as e:
            logger.error(f"Element not found: {e}")
            return None

    async def find_elements(
        self,
        selector: str,
        strategy: Optional[SelectorStrategy] = None,
    ) -> List[ElementHandle]:
        """Find all matching elements.

        Args:
            selector: Element selector
            strategy: Selector strategy

        Returns:
            List of element handles
        """
        try:
            if strategy == SelectorStrategy.XPATH:
                return await self.page.query_selector_all(f"xpath={selector}")
            elif strategy == SelectorStrategy.TEXT:
                return await self.page.query_selector_all(f"text={selector}")
            elif strategy == SelectorStrategy.ROLE:
                return await self.page.query_selector_all(f"role={selector}")
            else:
                return await self.page.query_selector_all(selector)
        except Exception as e:
            logger.error(f"Elements not found: {e}")
            return []

    async def generate_selector(
        self,
        element: ElementHandle,
        strategies: Optional[List[SelectorStrategy]] = None,
    ) -> List[SelectorInfo]:
        """Generate multiple selectors for element.

        Args:
            element: Target element
            strategies: Selector strategies to try

        Returns:
            List of selector info sorted by quality score
        """
        if strategies is None:
            strategies = [
                SelectorStrategy.ID,
                SelectorStrategy.TEST_ID,
                SelectorStrategy.ARIA,
                SelectorStrategy.CSS,
                SelectorStrategy.XPATH,
            ]

        selectors = []

        for strategy in strategies:
            if strategy == SelectorStrategy.ID:
                selector = await self._generate_id_selector(element)
                if selector:
                    selectors.append(selector)

            elif strategy == SelectorStrategy.TEST_ID:
                selector = await self._generate_test_id_selector(element)
                if selector:
                    selectors.append(selector)

            elif strategy == SelectorStrategy.ARIA:
                selector = await self._generate_aria_selector(element)
                if selector:
                    selectors.append(selector)

            elif strategy == SelectorStrategy.CSS:
                selector = await self._generate_css_selector(element)
                if selector:
                    selectors.append(selector)

            elif strategy == SelectorStrategy.XPATH:
                selector = await self._generate_xpath_selector(element)
                if selector:
                    selectors.append(selector)

        # Sort by score (descending)
        selectors.sort(key=lambda s: s.score, reverse=True)

        return selectors

    async def _generate_id_selector(
        self, element: ElementHandle
    ) -> Optional[SelectorInfo]:
        """Generate ID selector.

        Args:
            element: Target element

        Returns:
            Selector info or None
        """
        try:
            element_id = await element.get_attribute("id")
            if not element_id:
                return None

            selector = f"#{element_id}"
            unique = await self._is_unique(selector)

            return SelectorInfo(
                selector=selector,
                strategy=SelectorStrategy.ID,
                score=95.0 if unique else 70.0,
                unique=unique,
                stable=True,
            )
        except Exception:
            return None

    async def _generate_test_id_selector(
        self, element: ElementHandle
    ) -> Optional[SelectorInfo]:
        """Generate test ID selector.

        Args:
            element: Target element

        Returns:
            Selector info or None
        """
        try:
            # Try common test ID attributes
            for attr in ["data-testid", "data-test-id", "data-test"]:
                test_id = await element.get_attribute(attr)
                if test_id:
                    selector = f"[{attr}='{test_id}']"
                    unique = await self._is_unique(selector)

                    return SelectorInfo(
                        selector=selector,
                        strategy=SelectorStrategy.TEST_ID,
                        score=90.0 if unique else 65.0,
                        unique=unique,
                        stable=True,
                    )

            return None
        except Exception:
            return None

    async def _generate_aria_selector(
        self, element: ElementHandle
    ) -> Optional[SelectorInfo]:
        """Generate ARIA selector.

        Args:
            element: Target element

        Returns:
            Selector info or None
        """
        try:
            aria_label = await element.get_attribute("aria-label")
            if aria_label:
                selector = f"[aria-label='{aria_label}']"
                unique = await self._is_unique(selector)

                return SelectorInfo(
                    selector=selector,
                    strategy=SelectorStrategy.ARIA,
                    score=85.0 if unique else 60.0,
                    unique=unique,
                    stable=True,
                )

            return None
        except Exception:
            return None

    async def _generate_css_selector(
        self, element: ElementHandle
    ) -> Optional[SelectorInfo]:
        """Generate CSS selector.

        Args:
            element: Target element

        Returns:
            Selector info or None
        """
        try:
            # Get element info
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            class_name = await element.get_attribute("class")

            # Build CSS selector
            parts = [tag_name]

            if class_name:
                classes = class_name.strip().split()
                for cls in classes[:2]:  # Use max 2 classes
                    parts.append(f".{cls}")

            selector = "".join(parts)
            unique = await self._is_unique(selector)

            return SelectorInfo(
                selector=selector,
                strategy=SelectorStrategy.CSS,
                score=75.0 if unique else 50.0,
                unique=unique,
                stable=False,  # CSS selectors can be fragile
            )
        except Exception:
            return None

    async def _generate_xpath_selector(
        self, element: ElementHandle
    ) -> Optional[SelectorInfo]:
        """Generate XPath selector.

        Args:
            element: Target element

        Returns:
            Selector info or None
        """
        try:
            # Generate simple XPath
            xpath = await element.evaluate("""
                el => {
                    const getPathTo = (element) => {
                        if (element.id !== '')
                            return `//*[@id="${element.id}"]`;
                        if (element === document.body)
                            return '/html/body';

                        let ix = 0;
                        const siblings = element.parentNode.childNodes;
                        for (let i = 0; i < siblings.length; i++) {
                            const sibling = siblings[i];
                            if (sibling === element)
                                return getPathTo(element.parentNode) + '/' +
                                    element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            if (sibling.nodeType === 1 &&
                                sibling.tagName === element.tagName)
                                ix++;
                        }
                    };
                    return getPathTo(el);
                }
            """)

            return SelectorInfo(
                selector=xpath,
                strategy=SelectorStrategy.XPATH,
                score=65.0,
                unique=True,
                stable=False,  # XPath can be brittle
            )
        except Exception:
            return None

    async def _is_unique(self, selector: str) -> bool:
        """Check if selector matches exactly one element.

        Args:
            selector: CSS selector

        Returns:
            True if selector is unique
        """
        try:
            elements = await self.page.query_selector_all(selector)
            return len(elements) == 1
        except Exception:
            return False

    async def get_selector_with_fallback(
        self, element: ElementHandle
    ) -> List[str]:
        """Get selector with fallback options.

        Args:
            element: Target element

        Returns:
            List of selectors (best to worst)
        """
        selector_infos = await self.generate_selector(element)
        return [info.selector for info in selector_infos]

    async def validate_selector(
        self, selector: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate selector.

        Args:
            selector: Selector to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            element = await self.page.query_selector(selector)
            if element is None:
                return False, "Selector matches no elements"

            elements = await self.page.query_selector_all(selector)
            if len(elements) > 1:
                return True, f"Warning: Selector matches {len(elements)} elements"

            return True, None
        except Exception as e:
            return False, str(e)

    async def find_by_text(
        self,
        text: str,
        exact: bool = False,
        tag: Optional[str] = None,
    ) -> Optional[ElementHandle]:
        """Find element by text content.

        Args:
            text: Text to search for
            exact: Whether to match exact text
            tag: Optionally filter by tag name

        Returns:
            Element handle or None
        """
        try:
            if exact:
                selector = f"text='{text}'"
            else:
                selector = f"text={text}"

            if tag:
                selector = f"{tag}:has-text('{text}')"

            return await self.page.query_selector(selector)
        except Exception as e:
            logger.error(f"Find by text failed: {e}")
            return None

    async def find_by_role(
        self,
        role: str,
        name: Optional[str] = None,
    ) -> Optional[ElementHandle]:
        """Find element by ARIA role.

        Args:
            role: ARIA role (button, link, textbox, etc.)
            name: Accessible name

        Returns:
            Element handle or None
        """
        try:
            if name:
                selector = f"role={role}[name='{name}']"
            else:
                selector = f"role={role}"

            return await self.page.query_selector(selector)
        except Exception as e:
            logger.error(f"Find by role failed: {e}")
            return None
