"""
Theme management for OctoMaster Pro GUI.

This module provides theme management functionality including dark and light
themes with proper color palettes and utilities for theme switching.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication


class ThemeType(Enum):
    """Available theme types."""

    DARK = "dark"
    LIGHT = "light"


class ColorPalette:
    """Color palette for themes."""

    def __init__(
        self,
        background: str,
        foreground: str,
        primary: str,
        secondary: str,
        accent: str,
        success: str,
        warning: str,
        error: str,
        border: str,
        hover: str,
        disabled: str,
    ) -> None:
        """Initialize color palette.

        Args:
            background: Background color
            foreground: Foreground/text color
            primary: Primary color
            secondary: Secondary color
            accent: Accent color
            success: Success state color
            warning: Warning state color
            error: Error state color
            border: Border color
            hover: Hover state color
            disabled: Disabled state color
        """
        self.background = background
        self.foreground = foreground
        self.primary = primary
        self.secondary = secondary
        self.accent = accent
        self.success = success
        self.warning = warning
        self.error = error
        self.border = border
        self.hover = hover
        self.disabled = disabled


# Dark theme palette
DARK_PALETTE = ColorPalette(
    background="#1e1e1e",
    foreground="#d4d4d4",
    primary="#0e639c",
    secondary="#2d2d30",
    accent="#007acc",
    success="#4ec9b0",
    warning="#dcdcaa",
    error="#f48771",
    border="#3e3e42",
    hover="#2a2d2e",
    disabled="#656565",
)

# Light theme palette
LIGHT_PALETTE = ColorPalette(
    background="#ffffff",
    foreground="#000000",
    primary="#0078d4",
    secondary="#f3f3f3",
    accent="#005a9e",
    success="#107c10",
    warning="#fde300",
    error="#e81123",
    border="#d1d1d1",
    hover="#e5e5e5",
    disabled="#a6a6a6",
)


class ThemeManager(QObject):
    """Manages application themes and styling."""

    theme_changed = pyqtSignal(ThemeType)

    def __init__(self) -> None:
        """Initialize theme manager."""
        super().__init__()
        self._current_theme = ThemeType.DARK
        self._styles_dir = Path(__file__).parent

    @property
    def current_theme(self) -> ThemeType:
        """Get current theme.

        Returns:
            Current theme type
        """
        return self._current_theme

    @property
    def current_palette(self) -> ColorPalette:
        """Get current color palette.

        Returns:
            Color palette for current theme
        """
        return DARK_PALETTE if self._current_theme == ThemeType.DARK else LIGHT_PALETTE

    def set_theme(self, theme: ThemeType) -> None:
        """Set application theme.

        Args:
            theme: Theme type to apply
        """
        if theme == self._current_theme:
            return

        self._current_theme = theme
        self._apply_theme()
        self.theme_changed.emit(theme)

    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        new_theme = (
            ThemeType.LIGHT if self._current_theme == ThemeType.DARK else ThemeType.DARK
        )
        self.set_theme(new_theme)

    def _apply_theme(self) -> None:
        """Apply current theme to application."""
        app = QApplication.instance()
        if not app:
            return

        # Load and apply stylesheet
        stylesheet = self._load_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)

        # Set palette
        palette = self._create_qt_palette()
        app.setPalette(palette)

    def _load_stylesheet(self) -> Optional[str]:
        """Load QSS stylesheet for current theme.

        Returns:
            Stylesheet content or None if file not found
        """
        qss_file = self._styles_dir / f"{self._current_theme.value}.qss"

        if not qss_file.exists():
            return None

        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def _create_qt_palette(self) -> QPalette:
        """Create Qt palette from current color palette.

        Returns:
            QPalette configured for current theme
        """
        palette = QPalette()
        colors = self.current_palette

        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.foreground))

        # Base colors
        palette.setColor(QPalette.ColorRole.Base, QColor(colors.secondary))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.hover))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors.foreground))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(colors.secondary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.foreground))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.accent))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.accent))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors.primary))

        # Disabled colors
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            QColor(colors.disabled),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.Text,
            QColor(colors.disabled),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor(colors.disabled),
        )

        return palette

    def get_color(self, color_name: str) -> str:
        """Get color from current palette by name.

        Args:
            color_name: Name of color (e.g., 'primary', 'error')

        Returns:
            Color hex code

        Raises:
            AttributeError: If color name doesn't exist
        """
        return getattr(self.current_palette, color_name)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance.

    Returns:
        Global ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme(theme: ThemeType) -> None:
    """Apply theme to application.

    Args:
        theme: Theme type to apply
    """
    get_theme_manager().set_theme(theme)


def toggle_theme() -> None:
    """Toggle between dark and light themes."""
    get_theme_manager().toggle_theme()


def get_current_theme() -> ThemeType:
    """Get current theme type.

    Returns:
        Current theme type
    """
    return get_theme_manager().current_theme


def get_color(color_name: str) -> str:
    """Get color from current palette.

    Args:
        color_name: Name of color

    Returns:
        Color hex code
    """
    return get_theme_manager().get_color(color_name)
