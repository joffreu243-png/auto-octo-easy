"""
Element inspector for OctoMaster Pro.

Provides element highlighting, selector suggestion, and DOM inspection.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from loguru import logger

from playwright.async_api import Page, ElementHandle

from src.browser.selector_engine import SelectorEngine, SelectorInfo


@dataclass
class ElementInfo:
    """Information about inspected element."""

    tag_name: str
    attributes: Dict[str, str]
    text: Optional[str]
    selectors: List[SelectorInfo]
    bounding_box: Optional[Dict[str, float]]


class ElementInspector:
    """Element inspector for DOM inspection and highlighting."""

    def __init__(self, page: Page) -> None:
        """Initialize element inspector.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.selector_engine = SelectorEngine(page)
        self._highlighted_element: Optional[str] = None

    async def inspect_element(self, selector: str) -> Optional[ElementInfo]:
        """Inspect element and get detailed information.

        Args:
            selector: Element selector

        Returns:
            Element info or None if not found
        """
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return None

            # Get element details
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

            # Get attributes
            attributes = await element.evaluate("""
                el => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)

            # Get text content
            text = await element.text_content()

            # Generate selectors
            selectors = await self.selector_engine.generate_selector(element)

            # Get bounding box
            bounding_box = await element.bounding_box()

            return ElementInfo(
                tag_name=tag_name,
                attributes=attributes,
                text=text,
                selectors=selectors,
                bounding_box=bounding_box,
            )

        except Exception as e:
            logger.error(f"Element inspection failed: {e}")
            return None

    async def highlight_element(
        self,
        selector: str,
        color: str = "#ff0000",
        duration: Optional[int] = None,
    ) -> bool:
        """Highlight element on page.

        Args:
            selector: Element selector
            color: Highlight color
            duration: Highlight duration in ms (None = permanent)

        Returns:
            True if highlighted successfully
        """
        try:
            # Remove previous highlight
            await self.remove_highlight()

            # Add highlight
            await self.page.evaluate(f"""
                (selector) => {{
                    const element = document.querySelector(selector);
                    if (element) {{
                        element.style.outline = '3px solid {color}';
                        element.style.outlineOffset = '2px';
                        element.setAttribute('data-octo-highlighted', 'true');
                    }}
                }}
            """, selector)

            self._highlighted_element = selector

            # Auto-remove after duration
            if duration:
                await self.page.wait_for_timeout(duration)
                await self.remove_highlight()

            return True

        except Exception as e:
            logger.error(f"Highlight failed: {e}")
            return False

    async def remove_highlight(self) -> None:
        """Remove element highlighting."""
        try:
            await self.page.evaluate("""
                () => {
                    const highlighted = document.querySelector('[data-octo-highlighted]');
                    if (highlighted) {
                        highlighted.style.outline = '';
                        highlighted.style.outlineOffset = '';
                        highlighted.removeAttribute('data-octo-highlighted');
                    }
                }
            """)

            self._highlighted_element = None

        except Exception as e:
            logger.error(f"Remove highlight failed: {e}")

    async def get_element_path(self, selector: str) -> Optional[List[str]]:
        """Get DOM path to element.

        Args:
            selector: Element selector

        Returns:
            List of selectors from root to element
        """
        try:
            path = await self.page.evaluate(f"""
                (selector) => {{
                    const element = document.querySelector(selector);
                    if (!element) return null;

                    const path = [];
                    let current = element;

                    while (current && current !== document.body) {{
                        let selector = current.tagName.toLowerCase();

                        if (current.id) {{
                            selector += `#${{current.id}}`;
                        }} else if (current.className) {{
                            const classes = current.className.trim().split(/\\s+/);
                            if (classes.length > 0) {{
                                selector += '.' + classes.join('.');
                            }}
                        }}

                        path.unshift(selector);
                        current = current.parentElement;
                    }}

                    return path;
                }}
            """, selector)

            return path

        except Exception as e:
            logger.error(f"Get element path failed: {e}")
            return None

    async def get_computed_styles(
        self, selector: str, properties: Optional[List[str]] = None
    ) -> Optional[Dict[str, str]]:
        """Get computed CSS styles for element.

        Args:
            selector: Element selector
            properties: Specific properties to get (all if None)

        Returns:
            Dictionary of style properties
        """
        try:
            if properties:
                # Get specific properties
                styles = await self.page.evaluate(f"""
                    (selector, props) => {{
                        const element = document.querySelector(selector);
                        if (!element) return null;

                        const computed = window.getComputedStyle(element);
                        const result = {{}};

                        for (const prop of props) {{
                            result[prop] = computed.getPropertyValue(prop);
                        }}

                        return result;
                    }}
                """, selector, properties)
            else:
                # Get all properties
                styles = await self.page.evaluate(f"""
                    (selector) => {{
                        const element = document.querySelector(selector);
                        if (!element) return null;

                        const computed = window.getComputedStyle(element);
                        const result = {{}};

                        for (let i = 0; i < computed.length; i++) {{
                            const prop = computed[i];
                            result[prop] = computed.getPropertyValue(prop);
                        }}

                        return result;
                    }}
                """, selector)

            return styles

        except Exception as e:
            logger.error(f"Get computed styles failed: {e}")
            return None

    async def suggest_selectors(self, selector: str) -> List[SelectorInfo]:
        """Suggest alternative selectors for element.

        Args:
            selector: Current selector

        Returns:
            List of suggested selectors
        """
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return []

            return await self.selector_engine.generate_selector(element)

        except Exception as e:
            logger.error(f"Selector suggestion failed: {e}")
            return []
