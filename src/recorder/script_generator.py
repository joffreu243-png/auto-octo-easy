"""
Script generator for converting recorded actions to code.

Generates workflow blocks, Python code, and Playwright scripts.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from src.recorder.types import RecordedAction, ActionType, OptimizedAction


class ScriptGenerator:
    """Generates scripts from recorded actions."""

    def __init__(self) -> None:
        """Initialize script generator."""
        pass

    def generate_workflow_blocks(
        self, actions: List[RecordedAction]
    ) -> List[Dict[str, Any]]:
        """Generate node editor workflow blocks from actions.

        Args:
            actions: Recorded actions

        Returns:
            List of block configurations
        """
        blocks = []

        for i, action in enumerate(actions):
            block = self._action_to_block(action, i)
            if block:
                blocks.append(block)

        logger.info(f"Generated {len(blocks)} workflow blocks")
        return blocks

    def _action_to_block(
        self, action: RecordedAction, index: int
    ) -> Optional[Dict[str, Any]]:
        """Convert action to workflow block.

        Args:
            action: Recorded action
            index: Action index

        Returns:
            Block configuration or None
        """
        block = {
            "id": index,
            "position": {"x": 100, "y": 100 + (index * 100)},
        }

        if action.type == ActionType.NAVIGATE:
            block.update(
                {
                    "type": "OpenURLBlock",
                    "title": "Open URL",
                    "params": {"url": action.url or "", "wait_until": "domcontentloaded"},
                }
            )

        elif action.type == ActionType.CLICK:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "ClickBlock",
                    "title": "Click",
                    "params": {
                        "selector": selector,
                        "button": "left",
                        "click_count": 1,
                    },
                }
            )

        elif action.type == ActionType.DOUBLE_CLICK:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "ClickBlock",
                    "title": "Double Click",
                    "params": {
                        "selector": selector,
                        "button": "left",
                        "click_count": 2,
                    },
                }
            )

        elif action.type in [ActionType.TYPE_TEXT, ActionType.FILL]:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "FillBlock",
                    "title": "Fill",
                    "params": {"selector": selector, "text": action.value or ""},
                }
            )

        elif action.type == ActionType.SELECT:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "SelectDropdownBlock",
                    "title": "Select",
                    "params": {
                        "selector": selector,
                        "value": action.value or "",
                        "by": "value",
                    },
                }
            )

        elif action.type == ActionType.HOVER:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "HoverBlock",
                    "title": "Hover",
                    "params": {"selector": selector},
                }
            )

        elif action.type == ActionType.SCROLL:
            block.update(
                {
                    "type": "ScrollBlock",
                    "title": "Scroll",
                    "params": {
                        "x": action.position.get("x", 0) if action.position else 0,
                        "y": action.position.get("y", 0) if action.position else 0,
                    },
                }
            )

        elif action.type == ActionType.WAIT:
            block.update(
                {
                    "type": "WaitBlock",
                    "title": "Wait",
                    "params": {"duration": action.wait_time or 1.0},
                }
            )

        elif action.type == ActionType.WAIT_FOR_ELEMENT:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            block.update(
                {
                    "type": "WaitForElementBlock",
                    "title": "Wait For Element",
                    "params": {
                        "selector": selector,
                        "state": "visible",
                        "timeout": 30000,
                    },
                }
            )

        elif action.type == ActionType.SCREENSHOT:
            block.update(
                {
                    "type": "ScreenshotBlock",
                    "title": "Screenshot",
                    "params": {
                        "path": action.screenshot_path or "screenshot.png",
                        "full_page": False,
                    },
                }
            )

        else:
            return None

        return block

    def generate_python_playwright(
        self, actions: List[RecordedAction], filename: Optional[str] = None
    ) -> str:
        """Generate Python Playwright script.

        Args:
            actions: Recorded actions
            filename: Optional filename for script

        Returns:
            Python code as string
        """
        lines = [
            '"""',
            "Generated Playwright script.",
            f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Auto-generated by OctoMaster Pro Recorder.",
            '"""',
            "",
            "import asyncio",
            "from playwright.async_api import async_playwright, Page",
            "",
            "",
            "async def run(page: Page) -> None:",
            '    """Execute recorded workflow."""',
        ]

        for action in actions:
            action_code = self._action_to_playwright(action)
            if action_code:
                lines.extend(["    " + line for line in action_code])
                lines.append("")

        lines.extend(
            [
                "",
                "async def main() -> None:",
                '    """Main entry point."""',
                "    async with async_playwright() as p:",
                "        browser = await p.chromium.launch(headless=False)",
                "        context = await browser.new_context()",
                "        page = await context.new_page()",
                "",
                "        await run(page)",
                "",
                "        await context.close()",
                "        await browser.close()",
                "",
                "",
                'if __name__ == "__main__":',
                "    asyncio.run(main())",
            ]
        )

        code = "\n".join(lines)
        logger.info(f"Generated Python Playwright script ({len(lines)} lines)")

        return code

    def _action_to_playwright(self, action: RecordedAction) -> List[str]:
        """Convert action to Playwright code lines.

        Args:
            action: Recorded action

        Returns:
            List of code lines
        """
        lines = []

        # Add comment
        lines.append(f"# {action.type.value}")

        if action.type == ActionType.NAVIGATE:
            lines.append(f'await page.goto("{action.url}")')

        elif action.type == ActionType.CLICK:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            lines.append(f'await page.click("{selector}")')

        elif action.type == ActionType.DOUBLE_CLICK:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            lines.append(f'await page.dblclick("{selector}")')

        elif action.type in [ActionType.TYPE_TEXT, ActionType.FILL]:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            value = action.value or ""
            lines.append(f'await page.fill("{selector}", "{value}")')

        elif action.type == ActionType.SELECT:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            value = action.value or ""
            lines.append(f'await page.select_option("{selector}", value="{value}")')

        elif action.type == ActionType.HOVER:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            lines.append(f'await page.hover("{selector}")')

        elif action.type == ActionType.SCROLL:
            if action.position:
                x = action.position.get("x", 0)
                y = action.position.get("y", 0)
                lines.append(f"await page.evaluate(f'window.scrollTo({x}, {y})')")

        elif action.type == ActionType.WAIT:
            wait_time = action.wait_time or 1.0
            lines.append(f"await page.wait_for_timeout({int(wait_time * 1000)})")

        elif action.type == ActionType.WAIT_FOR_ELEMENT:
            selector = action.best_selector.to_playwright() if action.best_selector else ""
            lines.append(f'await page.wait_for_selector("{selector}")')

        elif action.type == ActionType.SCREENSHOT:
            path = action.screenshot_path or "screenshot.png"
            lines.append(f'await page.screenshot(path="{path}")')

        return lines

    def generate_python_selenium(self, actions: List[RecordedAction]) -> str:
        """Generate Python Selenium script.

        Args:
            actions: Recorded actions

        Returns:
            Python code as string
        """
        lines = [
            '"""',
            "Generated Selenium script.",
            f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Auto-generated by OctoMaster Pro Recorder.",
            '"""',
            "",
            "import time",
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "",
            "",
            "def run() -> None:",
            '    """Execute recorded workflow."""',
            "    driver = webdriver.Chrome()",
            "    wait = WebDriverWait(driver, 10)",
            "",
            "    try:",
        ]

        for action in actions:
            action_code = self._action_to_selenium(action)
            if action_code:
                lines.extend(["        " + line for line in action_code])
                lines.append("")

        lines.extend(
            [
                "    finally:",
                "        driver.quit()",
                "",
                "",
                'if __name__ == "__main__":',
                "    run()",
            ]
        )

        code = "\n".join(lines)
        logger.info(f"Generated Python Selenium script ({len(lines)} lines)")

        return code

    def _action_to_selenium(self, action: RecordedAction) -> List[str]:
        """Convert action to Selenium code lines.

        Args:
            action: Recorded action

        Returns:
            List of code lines
        """
        lines = []

        # Add comment
        lines.append(f"# {action.type.value}")

        if action.type == ActionType.NAVIGATE:
            lines.append(f'driver.get("{action.url}")')

        elif action.type == ActionType.CLICK:
            selector = self._selector_to_selenium_by(action.best_selector)
            if selector:
                by, value = selector
                lines.append(f'element = wait.until(EC.element_to_be_clickable(({by}, "{value}")))')
                lines.append("element.click()")

        elif action.type in [ActionType.TYPE_TEXT, ActionType.FILL]:
            selector = self._selector_to_selenium_by(action.best_selector)
            if selector:
                by, value = selector
                val = action.value or ""
                lines.append(f'element = wait.until(EC.presence_of_element_located(({by}, "{value}")))')
                lines.append("element.clear()")
                lines.append(f'element.send_keys("{val}")')

        elif action.type == ActionType.WAIT:
            wait_time = action.wait_time or 1.0
            lines.append(f"time.sleep({wait_time})")

        return lines

    def _selector_to_selenium_by(self, selector) -> Optional[tuple]:
        """Convert selector to Selenium By.

        Args:
            selector: Selector object

        Returns:
            Tuple of (By constant, value) or None
        """
        if not selector:
            return None

        from src.recorder.types import SelectorType

        if selector.type == SelectorType.ID:
            return ("By.ID", selector.value)
        elif selector.type == SelectorType.CLASS:
            return ("By.CLASS_NAME", selector.value)
        elif selector.type == SelectorType.CSS:
            return ("By.CSS_SELECTOR", selector.value)
        elif selector.type == SelectorType.XPATH:
            return ("By.XPATH", selector.value)
        elif selector.type == SelectorType.NAME:
            return ("By.NAME", selector.value)
        else:
            # Default to CSS selector
            return ("By.CSS_SELECTOR", selector.to_playwright())

    def save_to_file(self, code: str, file_path: Path) -> bool:
        """Save generated code to file.

        Args:
            code: Generated code
            file_path: Output file path

        Returns:
            True if successful
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            logger.info(f"Script saved to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save script: {e}")
            return False
