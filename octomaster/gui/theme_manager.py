"""
Theme manager for OctoMaster Pro.

Manages application themes and provides default themes.
"""

from typing import Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from loguru import logger

from octomaster.core.plugins.manager import PluginManager
from octomaster.core.plugins.plugin import PluginType


@dataclass
class Theme:
    """Theme definition."""

    id: str
    name: str
    description: str
    stylesheet: str
    colors: Dict[str, str]
    is_dark: bool = False


class ThemeManager:
    """Manages application themes."""

    def __init__(self, app: Optional[QApplication] = None, plugin_manager: Optional[PluginManager] = None):
        """
        Initialize theme manager.

        Args:
            app: QApplication instance
            plugin_manager: Plugin manager for loading theme plugins
        """
        self.app = app
        self.plugin_manager = plugin_manager
        self.themes: Dict[str, Theme] = {}
        self.current_theme_id: Optional[str] = None

        # Register default themes
        self._register_default_themes()

        # Load theme plugins if available
        if self.plugin_manager:
            self._load_theme_plugins()

    def _register_default_themes(self):
        """Register default built-in themes."""
        # Light theme
        light_theme = Theme(
            id="light",
            name="Light",
            description="Default light theme",
            stylesheet=self._get_light_stylesheet(),
            colors={
                "background": "#ffffff",
                "foreground": "#000000",
                "accent": "#0078d4",
                "border": "#cccccc",
            },
            is_dark=False,
        )
        self.themes["light"] = light_theme

        # Dark theme
        dark_theme = Theme(
            id="dark",
            name="Dark",
            description="Default dark theme",
            stylesheet=self._get_dark_stylesheet(),
            colors={
                "background": "#1e1e1e",
                "foreground": "#cccccc",
                "accent": "#007acc",
                "border": "#3e3e42",
            },
            is_dark=True,
        )
        self.themes["dark"] = dark_theme

    def _load_theme_plugins(self):
        """Load theme plugins."""
        if not self.plugin_manager:
            return

        theme_plugins = self.plugin_manager.get_plugins_by_type(PluginType.THEME)

        for plugin in theme_plugins:
            try:
                theme = Theme(
                    id=plugin.metadata.id,
                    name=plugin.metadata.name,
                    description=plugin.metadata.description,
                    stylesheet=plugin.get_stylesheet(),
                    colors=plugin.get_colors(),
                    is_dark=plugin.get_colors().get("background", "#fff").lower() < "#888",
                )
                self.themes[theme.id] = theme
                logger.info(f"Loaded theme plugin: {theme.name}")

            except Exception as e:
                logger.error(f"Error loading theme plugin {plugin.metadata.id}: {e}")

    def apply_theme(self, theme_id: str) -> bool:
        """
        Apply a theme.

        Args:
            theme_id: Theme ID

        Returns:
            True if successful
        """
        if theme_id not in self.themes:
            logger.error(f"Theme not found: {theme_id}")
            return False

        theme = self.themes[theme_id]

        try:
            if self.app:
                # Apply stylesheet
                self.app.setStyleSheet(theme.stylesheet)

                # Update palette for native widgets
                if theme.is_dark:
                    self._apply_dark_palette()
                else:
                    self._apply_light_palette()

            self.current_theme_id = theme_id
            logger.info(f"Applied theme: {theme.name}")
            return True

        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            return False

    def _apply_dark_palette(self):
        """Apply dark color palette."""
        if not self.app:
            return

        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(204, 204, 204))

        # Base colors
        palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 38))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(37, 37, 38))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(204, 204, 204))

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(204, 204, 204))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(133, 133, 133))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(37, 37, 38))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(204, 204, 204))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(55, 148, 255))

        self.app.setPalette(palette)

    def _apply_light_palette(self):
        """Apply light color palette."""
        if not self.app:
            return

        # Reset to default light palette
        palette = QPalette()
        self.app.setPalette(palette)

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """
        Get a theme by ID.

        Args:
            theme_id: Theme ID

        Returns:
            Theme or None
        """
        return self.themes.get(theme_id)

    def get_current_theme(self) -> Optional[Theme]:
        """
        Get current theme.

        Returns:
            Current theme or None
        """
        if self.current_theme_id:
            return self.themes.get(self.current_theme_id)
        return None

    def list_themes(self) -> List[Dict[str, str]]:
        """
        List available themes.

        Returns:
            List of theme info
        """
        return [
            {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "is_dark": str(theme.is_dark),
            }
            for theme in self.themes.values()
        ]

    def _get_light_stylesheet(self) -> str:
        """Get light theme stylesheet."""
        return """
        /* Light Theme */
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }

        QMenuBar {
            background-color: #f3f3f3;
            color: #000000;
        }

        QMenuBar::item:selected {
            background-color: #e5e5e5;
        }

        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }

        QMenu::item:selected {
            background-color: #0078d4;
            color: white;
        }

        QPushButton {
            background-color: #f3f3f3;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 6px 12px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #e5e5e5;
            border-color: #0078d4;
        }

        QPushButton:pressed {
            background-color: #d0d0d0;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 4px 8px;
            border-radius: 3px;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #0078d4;
        }

        QTreeView {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }

        QTreeView::item:selected {
            background-color: #0078d4;
            color: white;
        }

        QTreeView::item:hover {
            background-color: #e5e5e5;
        }

        QToolBar {
            background-color: #f3f3f3;
            border-bottom: 1px solid #cccccc;
        }

        QStatusBar {
            background-color: #f3f3f3;
            color: #000000;
            border-top: 1px solid #cccccc;
        }
        """

    def _get_dark_stylesheet(self) -> str:
        """Get dark theme stylesheet."""
        return """
        /* Dark Theme */
        QMainWindow {
            background-color: #1e1e1e;
            color: #cccccc;
        }

        QMenuBar {
            background-color: #2d2d30;
            color: #cccccc;
        }

        QMenuBar::item:selected {
            background-color: #3e3e42;
        }

        QMenu {
            background-color: #252526;
            color: #cccccc;
            border: 1px solid #3e3e42;
        }

        QMenu::item:selected {
            background-color: #007acc;
            color: white;
        }

        QPushButton {
            background-color: #2d2d30;
            color: #cccccc;
            border: 1px solid #3e3e42;
            padding: 6px 12px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #3e3e42;
            border-color: #007acc;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #252526;
            color: #cccccc;
            border: 1px solid #3e3e42;
            padding: 4px 8px;
            border-radius: 3px;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #007acc;
        }

        QComboBox {
            background-color: #252526;
            color: #cccccc;
            border: 1px solid #3e3e42;
            padding: 4px 8px;
            border-radius: 3px;
        }

        QComboBox:hover {
            border-color: #007acc;
        }

        QTreeView {
            background-color: #1e1e1e;
            color: #cccccc;
            border: 1px solid #3e3e42;
        }

        QTreeView::item:selected {
            background-color: #007acc;
            color: white;
        }

        QTreeView::item:hover {
            background-color: #2a2d2e;
        }

        QSplitter::handle {
            background-color: #3e3e42;
        }

        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 12px;
        }

        QScrollBar::handle:vertical {
            background-color: #3e3e42;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #5a5a5a;
        }

        QToolBar {
            background-color: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            spacing: 4px;
        }

        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
        }

        QToolButton:hover {
            background-color: #3e3e42;
        }

        QStatusBar {
            background-color: #2d2d30;
            color: #cccccc;
            border-top: 1px solid #3e3e42;
        }

        QGraphicsView {
            background-color: #1e1e1e;
            border: none;
        }

        QTabWidget::pane {
            border: 1px solid #3e3e42;
        }

        QTabBar::tab {
            background-color: #2d2d30;
            color: #cccccc;
            padding: 8px 16px;
            border: 1px solid #3e3e42;
        }

        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 2px solid #007acc;
        }

        QTabBar::tab:hover {
            background-color: #3e3e42;
        }
        """
