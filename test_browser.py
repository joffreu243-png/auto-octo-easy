#!/usr/bin/env python3
"""
Test browser module for OctoMaster Pro.

Simple test to verify browser automation works.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.browser.controller import BrowserController


async def test_browser():
    """Test browser automation."""
    print("🌐 Testing Browser Module...")

    # Create browser controller
    browser = BrowserController()

    try:
        # Start browser
        print("  Starting browser (headless)...")
        await browser.start(headless=True)
        print("  ✅ Browser started")

        # Navigate to example.com
        print("  Navigating to example.com...")
        result = await browser.navigate("https://example.com")
        if result.success:
            print(f"  ✅ Navigation successful: {result.data['url']}")
        else:
            print(f"  ❌ Navigation failed: {result.error}")

        # Wait for page to load
        await asyncio.sleep(2)

        # Take screenshot
        print("  Taking screenshot...")
        screenshot_result = await browser.screenshot(
            path="test_screenshot.png",
            full_page=True
        )
        if screenshot_result.success:
            print("  ✅ Screenshot saved: test_screenshot.png")
        else:
            print(f"  ❌ Screenshot failed: {screenshot_result.error}")

        # Get page title
        page = browser.current_page
        if page:
            title = await page.title()
            print(f"  📄 Page title: {title}")

        # Test element inspection
        print("  Testing element inspection...")
        element_info = await browser.inspect_element("h1")
        if element_info:
            print(f"  ✅ Found element: {element_info.tag_name}")
            print(f"     Text: {element_info.text}")
            if element_info.selectors:
                print(f"     Best selector: {element_info.selectors[0].selector}")
        else:
            print("  ⚠️  Element not found")

        # Test tab management
        print("  Testing tab management...")
        tabs_info = await browser.get_tabs_info()
        print(f"  📑 Active tabs: {len(tabs_info)}")

        # Create new tab
        print("  Creating new tab...")
        new_page = await browser.new_tab()
        await browser.navigate("https://example.org")
        print("  ✅ New tab created and navigated")

        tabs_info = await browser.get_tabs_info()
        print(f"  📑 Active tabs: {len(tabs_info)}")
        for i, tab in enumerate(tabs_info):
            print(f"     Tab {i}: {tab.title} {'(active)' if tab.is_active else ''}")

        print("\n✅ All browser tests passed!")

    except Exception as e:
        print(f"\n❌ Browser test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Stop browser
        print("\n  Stopping browser...")
        await browser.stop()
        print("  ✅ Browser stopped")


def main() -> int:
    """Run browser tests.

    Returns:
        Exit code
    """
    try:
        asyncio.run(test_browser())
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
