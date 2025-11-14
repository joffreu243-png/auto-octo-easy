"""
Console Widget.

Displays output, logs, and errors from workflow execution.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QToolBar, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QFont, QColor, QTextCharFormat
from datetime import datetime


class ConsoleWidget(QWidget):
    """Console widget for displaying logs and output."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear)
        toolbar.addWidget(clear_btn)

        toolbar.addSeparator()

        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_logs)
        toolbar.addWidget(export_btn)

        layout.addWidget(toolbar)

        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 9))
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
            }
        """
        )

        layout.addWidget(self.text_edit)

    def append_text(self, text: str, color: str = None):
        """Append text to console."""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set color if provided
        if color:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)

        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def append_info(self, message: str):
        """Append info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(f"[{timestamp}] ", "#808080")
        self.append_text("INFO: ", "#4EC9B0")
        self.append_text(f"{message}\n", "#D4D4D4")

    def append_warning(self, message: str):
        """Append warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(f"[{timestamp}] ", "#808080")
        self.append_text("WARNING: ", "#FFC107")
        self.append_text(f"{message}\n", "#D4D4D4")

    def append_error(self, message: str):
        """Append error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(f"[{timestamp}] ", "#808080")
        self.append_text("ERROR: ", "#F44336")
        self.append_text(f"{message}\n", "#D4D4D4")

    def append_success(self, message: str):
        """Append success message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(f"[{timestamp}] ", "#808080")
        self.append_text("SUCCESS: ", "#4CAF50")
        self.append_text(f"{message}\n", "#D4D4D4")

    def clear(self):
        """Clear the console."""
        self.text_edit.clear()

    def export_logs(self):
        """Export logs to file."""
        # TODO: Implement log export
        self.append_info("Export logs not implemented yet")
