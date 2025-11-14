"""
Smart selector generation for recorded elements.

Generates multiple selector strategies and ranks them by quality.
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from src.recorder.types import Selector, SelectorType, ElementInfo


class SelectorGenerator:
    """Generates and ranks element selectors."""

    def __init__(self) -> None:
        """Initialize selector generator."""
        # Selector weights for scoring
        self.weights = {
            SelectorType.ID: 100,
            SelectorType.DATA_TESTID: 95,
            SelectorType.DATA_QA: 90,
            SelectorType.ARIA_LABEL: 85,
            SelectorType.NAME: 80,
            SelectorType.PLACEHOLDER: 75,
            SelectorType.ROLE: 70,
            SelectorType.TEXT: 60,
            SelectorType.CLASS: 40,
            SelectorType.CSS: 30,
            SelectorType.XPATH: 20,
        }

    async def generate_selectors(
        self, element_info: ElementInfo, page: Any
    ) -> List[Selector]:
        """Generate all possible selectors for element.

        Args:
            element_info: Element information
            page: Playwright page instance

        Returns:
            List of selectors ranked by quality
        """
        selectors: List[Selector] = []

        # Generate selectors for each strategy
        if element_info.id:
            selector = await self._generate_id_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.data_testid:
            selector = await self._generate_data_testid_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.data_qa:
            selector = await self._generate_data_qa_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.aria_label:
            selector = await self._generate_aria_label_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.name:
            selector = await self._generate_name_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.placeholder:
            selector = await self._generate_placeholder_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.role:
            selector = await self._generate_role_selector(element_info, page)
            if selector:
                selectors.append(selector)

        if element_info.text:
            selector = await self._generate_text_selector(element_info, page)
            if selector:
                selectors.append(selector)

        # Class selector
        if element_info.classes:
            selector = await self._generate_class_selector(element_info, page)
            if selector:
                selectors.append(selector)

        # CSS path
        if element_info.css_path:
            selector = await self._generate_css_selector(element_info, page)
            if selector:
                selectors.append(selector)

        # XPath (fallback)
        if element_info.xpath:
            selector = await self._generate_xpath_selector(element_info, page)
            if selector:
                selectors.append(selector)

        # Sort by score (highest first)
        selectors.sort(key=lambda s: s.score, reverse=True)

        logger.debug(f"Generated {len(selectors)} selectors for {element_info.tag_name}")

        return selectors

    async def _generate_id_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate ID selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.id:
            return None

        selector_str = f"#{element_info.id}"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.ID]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.ID,
            value=element_info.id,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_data_testid_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate data-testid selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.data_testid:
            return None

        selector_str = f"[data-testid='{element_info.data_testid}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.DATA_TESTID]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.DATA_TESTID,
            value=element_info.data_testid,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_data_qa_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate data-qa selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.data_qa:
            return None

        selector_str = f"[data-qa='{element_info.data_qa}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.DATA_QA]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.DATA_QA,
            value=element_info.data_qa,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_aria_label_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate aria-label selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.aria_label:
            return None

        selector_str = f"[aria-label='{element_info.aria_label}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.ARIA_LABEL]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.ARIA_LABEL,
            value=element_info.aria_label,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_name_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate name attribute selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.name:
            return None

        selector_str = f"[name='{element_info.name}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.NAME]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.NAME,
            value=element_info.name,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_placeholder_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate placeholder selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.placeholder:
            return None

        selector_str = f"[placeholder='{element_info.placeholder}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.PLACEHOLDER]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.PLACEHOLDER,
            value=element_info.placeholder,
            score=score,
            is_unique=is_unique,
            is_stable=False,  # Placeholder text might change
        )

    async def _generate_role_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate role selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.role:
            return None

        selector_str = f"[role='{element_info.role}']"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.ROLE]
        # Role alone is rarely unique
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.ROLE,
            value=element_info.role,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )

    async def _generate_text_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate text content selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.text or len(element_info.text.strip()) == 0:
            return None

        # Trim long text
        text = element_info.text.strip()
        if len(text) > 50:
            text = text[:50]

        selector_str = f"text={text}"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.TEXT]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.TEXT,
            value=text,
            score=score,
            is_unique=is_unique,
            is_stable=False,  # Text content might change
        )

    async def _generate_class_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate class selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.classes:
            return None

        # Use most specific classes (avoid generic like 'btn', 'container')
        specific_classes = [
            c for c in element_info.classes if len(c) > 3 and "-" in c or "_" in c
        ]

        if specific_classes:
            class_str = ".".join(specific_classes[:2])  # Max 2 classes
        else:
            class_str = ".".join(element_info.classes[:2])

        selector_str = f".{class_str}"
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.CLASS]
        if is_unique:
            score += 20

        return Selector(
            type=SelectorType.CLASS,
            value=class_str,
            score=score,
            is_unique=is_unique,
            is_stable=False,  # Classes might change
        )

    async def _generate_css_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate CSS path selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.css_path:
            return None

        selector_str = element_info.css_path
        is_unique = await self._check_uniqueness(selector_str, page)

        score = self.weights[SelectorType.CSS]
        if is_unique:
            score += 15

        return Selector(
            type=SelectorType.CSS,
            value=element_info.css_path,
            score=score,
            is_unique=is_unique,
            is_stable=False,  # CSS path can break easily
        )

    async def _generate_xpath_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate XPath selector.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Selector or None
        """
        if not element_info.xpath:
            return None

        selector_str = element_info.xpath
        # XPath needs special handling in check_uniqueness
        try:
            count = await page.locator(f"xpath={selector_str}").count()
            is_unique = count == 1
        except Exception:
            is_unique = False

        score = self.weights[SelectorType.XPATH]
        if is_unique:
            score += 10

        return Selector(
            type=SelectorType.XPATH,
            value=element_info.xpath,
            score=score,
            is_unique=is_unique,
            is_stable=False,  # XPath is very fragile
        )

    async def _check_uniqueness(self, selector: str, page: Any) -> bool:
        """Check if selector matches exactly one element.

        Args:
            selector: Selector string
            page: Playwright page

        Returns:
            True if unique
        """
        try:
            count = await page.locator(selector).count()
            return count == 1
        except Exception as e:
            logger.debug(f"Failed to check uniqueness for {selector}: {e}")
            return False

    def get_best_selector(self, selectors: List[Selector]) -> Optional[Selector]:
        """Get best selector from list.

        Args:
            selectors: List of selectors

        Returns:
            Best selector or None
        """
        if not selectors:
            return None

        # Prefer unique and stable selectors
        unique_stable = [s for s in selectors if s.is_unique and s.is_stable]
        if unique_stable:
            return unique_stable[0]

        # Then unique selectors
        unique = [s for s in selectors if s.is_unique]
        if unique:
            return unique[0]

        # Finally, highest score
        return selectors[0] if selectors else None

    async def generate_combined_selector(
        self, element_info: ElementInfo, page: Any
    ) -> Optional[Selector]:
        """Generate combined selector using multiple attributes.

        Args:
            element_info: Element information
            page: Playwright page

        Returns:
            Combined selector or None
        """
        parts = []

        # Start with tag
        parts.append(element_info.tag_name)

        # Add most specific attributes
        if element_info.id:
            parts.append(f"#{element_info.id}")
        elif element_info.data_testid:
            parts.append(f"[data-testid='{element_info.data_testid}']")
        elif element_info.classes:
            specific = [c for c in element_info.classes if len(c) > 3]
            if specific:
                parts.append(f".{specific[0]}")

        # Combine
        selector_str = "".join(parts)

        is_unique = await self._check_uniqueness(selector_str, page)

        score = 50  # Base score for combined
        if is_unique:
            score += 30

        return Selector(
            type=SelectorType.CSS,
            value=selector_str,
            score=score,
            is_unique=is_unique,
            is_stable=True,
        )
