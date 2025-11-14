"""
Browser automation module for OctoMaster Pro.

Complete browser automation with Playwright integration, element inspection,
selector engine, and Qt WebEngine view.
"""

from src.browser.controller import BrowserController
from src.browser.playwright_bridge import PlaywrightBridge
from src.browser.actions import BrowserActions, ActionResult, MouseButton, KeyModifier
from src.browser.selector_engine import SelectorEngine, SelectorStrategy, SelectorInfo
from src.browser.cdp_client import CDPClient
from src.browser.tab_manager import TabManager, TabInfo
from src.browser.inspector import ElementInspector, ElementInfo
from src.browser.webengine_view import WebEngineView

__all__ = [
    "BrowserController",
    "PlaywrightBridge",
    "BrowserActions",
    "ActionResult",
    "MouseButton",
    "KeyModifier",
    "SelectorEngine",
    "SelectorStrategy",
    "SelectorInfo",
    "CDPClient",
    "TabManager",
    "TabInfo",
    "ElementInspector",
    "ElementInfo",
    "WebEngineView",
]
