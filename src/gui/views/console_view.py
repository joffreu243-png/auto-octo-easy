"""
Console view for OctoMaster Pro.

Provides a console output widget with colored messages.
"""

from typing import Optional
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPlainTextEdit


class ConsoleView(QWidget):
    """Console output widget with colored messages."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize console view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._console = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self._console)

        # Set monospace font
        from PyQt6.QtGui import QFont

        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._console.setFont(font)

    def log(self, message: str, level: str = "info") -> None:
        """Log message to console.

        Args:
            message: Message to log
            level: Log level (info, warning, error, success, debug)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color based on level
        colors = {
            "info": QColor(200, 200, 200),
            "warning": QColor(255, 200, 0),
            "error": QColor(255, 100, 100),
            "success": QColor(100, 255, 100),
            "debug": QColor(150, 150, 150),
        }

        # Icon based on level
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "debug": "🔍",
        }

        color = colors.get(level, colors["info"])
        icon = icons.get(level, "")

        # Format message
        cursor = self._console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add timestamp
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(128, 128, 128))
        cursor.insertText(f"[{timestamp}] ", fmt)

        # Add icon and message
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.insertText(f"{icon} {message}\n", fmt)

        # Scroll to bottom
        self._console.setTextCursor(cursor)
        self._console.ensureCursorVisible()

    def info(self, message: str) -> None:
        """Log info message.

        Args:
            message: Message to log
        """
        self.log(message, "info")

    def warning(self, message: str) -> None:
        """Log warning message.

        Args:
            message: Message to log
        """
        self.log(message, "warning")

    def error(self, message: str) -> None:
        """Log error message.

        Args:
            message: Message to log
        """
        self.log(message, "error")

    def success(self, message: str) -> None:
        """Log success message.

        Args:
            message: Message to log
        """
        self.log(message, "success")

    def debug(self, message: str) -> None:
        """Log debug message.

        Args:
            message: Message to log
        """
        self.log(message, "debug")

    def clear(self) -> None:
        """Clear console."""
        self._console.clear()

    def get_text(self) -> str:
        """Get console text.

        Returns:
            Console text
        """
        return self._console.toPlainText()
