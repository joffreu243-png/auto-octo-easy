"""
Dark Theme Plugin for OctoMaster Pro.

Provides a modern dark color scheme.
"""

from typing import Dict
from pathlib import Path
from loguru import logger

from octomaster.core.plugins.plugin import ThemePlugin, PluginMetadata


class PluginClass(ThemePlugin):
    """Dark theme plugin implementation."""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.colors = {}
        self.stylesheet = ""

    def initialize(self) -> bool:
        """Initialize plugin."""
        try:
            logger.info(f"Initializing {self.metadata.name}")

            # Define color palette
            accent = self.get_config("accent_color", "#007acc")

            self.colors = {
                # Background colors
                "background": "#1e1e1e",
                "background_alt": "#252526",
                "background_selected": "#37373d",

                # Foreground colors
                "foreground": "#cccccc",
                "foreground_dim": "#858585",

                # Accent colors
                "accent": accent,
                "accent_hover": "#005a9e",
                "accent_pressed": "#004578",

                # Border colors
                "border": "#3e3e42",
                "border_focus": accent,

                # Status colors
                "success": "#89d185",
                "warning": "#f0ad4e",
                "error": "#f44747",
                "info": "#3794ff",

                # Syntax highlighting
                "syntax_keyword": "#569cd6",
                "syntax_string": "#ce9178",
                "syntax_number": "#b5cea8",
                "syntax_comment": "#6a9955",
                "syntax_function": "#dcdcaa",
            }

            # Generate stylesheet
            self.stylesheet = self._generate_stylesheet()

            logger.info(f"Theme initialized with accent color: {accent}")
            return True

        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}")
            return False

    def activate(self) -> bool:
        """Activate plugin."""
        try:
            logger.info(f"Activating {self.metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Plugin activation failed: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate plugin."""
        try:
            logger.info(f"Deactivating {self.metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Plugin deactivation failed: {e}")
            return False

    def get_stylesheet(self) -> str:
        """Get Qt stylesheet."""
        return self.stylesheet

    def get_colors(self) -> Dict[str, str]:
        """Get theme colors."""
        return self.colors

    def get_icons(self) -> Dict[str, Path]:
        """Get theme icons."""
        # Return default icons for now
        return {}

    def _generate_stylesheet(self) -> str:
        """Generate Qt stylesheet from colors."""
        c = self.colors

        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {c['background']};
            color: {c['foreground']};
        }}

        /* Widgets */
        QWidget {{
            background-color: {c['background']};
            color: {c['foreground']};
            border: none;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c['background_alt']};
            color: {c['foreground']};
            border: 1px solid {c['border']};
            padding: 6px 12px;
            border-radius: 3px;
        }}

        QPushButton:hover {{
            background-color: {c['background_selected']};
            border-color: {c['accent']};
        }}

        QPushButton:pressed {{
            background-color: {c['accent_pressed']};
        }}

        /* Primary Button */
        QPushButton[primary="true"] {{
            background-color: {c['accent']};
            color: white;
            border: none;
        }}

        QPushButton[primary="true"]:hover {{
            background-color: {c['accent_hover']};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['background_alt']};
            color: {c['foreground']};
            border: 1px solid {c['border']};
            padding: 4px 8px;
            border-radius: 3px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['border_focus']};
        }}

        /* ComboBox */
        QComboBox {{
            background-color: {c['background_alt']};
            color: {c['foreground']};
            border: 1px solid {c['border']};
            padding: 4px 8px;
            border-radius: 3px;
        }}

        QComboBox:hover {{
            border-color: {c['accent']};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        /* Menu */
        QMenuBar {{
            background-color: {c['background']};
            color: {c['foreground']};
        }}

        QMenuBar::item:selected {{
            background-color: {c['background_selected']};
        }}

        QMenu {{
            background-color: {c['background_alt']};
            color: {c['foreground']};
            border: 1px solid {c['border']};
        }}

        QMenu::item:selected {{
            background-color: {c['accent']};
            color: white;
        }}

        /* Tree View */
        QTreeView {{
            background-color: {c['background']};
            color: {c['foreground']};
            border: 1px solid {c['border']};
        }}

        QTreeView::item:selected {{
            background-color: {c['accent']};
            color: white;
        }}

        QTreeView::item:hover {{
            background-color: {c['background_selected']};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {c['border']};
        }}

        /* Scrollbar */
        QScrollBar:vertical {{
            background-color: {c['background']};
            width: 12px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['background_selected']};
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['foreground_dim']};
        }}

        /* Toolbar */
        QToolBar {{
            background-color: {c['background_alt']};
            border-bottom: 1px solid {c['border']};
            spacing: 4px;
        }}

        QToolButton {{
            background-color: transparent;
            border: none;
            padding: 4px;
        }}

        QToolButton:hover {{
            background-color: {c['background_selected']};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {c['background_alt']};
            color: {c['foreground']};
            border-top: 1px solid {c['border']};
        }}

        /* Graphics View */
        QGraphicsView {{
            background-color: {c['background']};
            border: none;
        }}
        """
