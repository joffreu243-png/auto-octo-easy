"""GUI views module."""

from src.gui.views.canvas_view import CanvasView
from src.gui.views.code_view import CodeView, CodeEditor
from src.gui.views.browser_view import BrowserView
from src.gui.views.console_view import ConsoleView

__all__ = [
    "CanvasView",
    "CodeView",
    "CodeEditor",
    "BrowserView",
    "ConsoleView",
]
