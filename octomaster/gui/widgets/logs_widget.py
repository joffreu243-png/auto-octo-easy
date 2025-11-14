"""
Logs Widget for OctoMaster Pro.

Displays application and workflow execution logs in real-time.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont
from datetime import datetime
from loguru import logger


class LogsWidget(QWidget):
    """Widget for displaying logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_buffer = []
        self.max_logs = 1000
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar
        toolbar = QHBoxLayout()

        # Log level filter
        toolbar.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.setCurrentText("INFO")
        self.level_filter.currentTextChanged.connect(self.apply_filter)
        toolbar.addWidget(self.level_filter)

        toolbar.addSpacing(10)

        # Auto-scroll checkbox
        self.auto_scroll = QCheckBox("Auto-scroll")
        self.auto_scroll.setChecked(True)
        toolbar.addWidget(self.auto_scroll)

        # Word wrap checkbox
        self.word_wrap = QCheckBox("Word wrap")
        self.word_wrap.setChecked(False)
        self.word_wrap.toggled.connect(self.toggle_word_wrap)
        toolbar.addWidget(self.word_wrap)

        toolbar.addStretch()

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(clear_btn)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_logs)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.log_text)

    def append_log(self, level: str, message: str, timestamp: datetime = None):
        """
        Append a log message.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            timestamp: Timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Store in buffer
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.log_buffer.append(log_entry)

        # Limit buffer size
        if len(self.log_buffer) > self.max_logs:
            self.log_buffer.pop(0)

        # Check if should display based on filter
        current_filter = self.level_filter.currentText()
        if current_filter != "ALL":
            level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level_order.index(level) < level_order.index(current_filter):
                return

        # Format and append
        formatted = f"[{timestamp.strftime('%H:%M:%S')}] [{level:8}] {message}"

        # Set color based on level
        color_map = {
            "DEBUG": QColor("#6c757d"),
            "INFO": QColor("#007bff"),
            "WARNING": QColor("#ffc107"),
            "ERROR": QColor("#dc3545"),
            "CRITICAL": QColor("#bd2130"),
        }

        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(color_map.get(level, QColor("#000000")))

        cursor.insertText(formatted + "\n", fmt)

        # Auto-scroll
        if self.auto_scroll.isChecked():
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )

    @pyqtSlot()
    def clear_logs(self):
        """Clear all logs."""
        self.log_text.clear()
        self.log_buffer.clear()
        logger.debug("Logs cleared")

    @pyqtSlot()
    def export_logs(self):
        """Export logs to file."""
        from PyQt6.QtWidgets import QFileDialog
        from pathlib import Path

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for entry in self.log_buffer:
                        f.write(f"[{entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] "
                               f"[{entry['level']:8}] {entry['message']}\n")
                logger.info(f"Logs exported to {file_path}")
            except Exception as e:
                logger.error(f"Failed to export logs: {e}")

    @pyqtSlot(str)
    def apply_filter(self, level: str):
        """Apply log level filter."""
        # Rebuild display from buffer
        self.log_text.clear()

        level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        min_index = 0 if level == "ALL" else level_order.index(level)

        for entry in self.log_buffer:
            if level == "ALL" or level_order.index(entry["level"]) >= min_index:
                self.append_log(entry["level"], entry["message"], entry["timestamp"])

    @pyqtSlot(bool)
    def toggle_word_wrap(self, enabled: bool):
        """Toggle word wrap."""
        if enabled:
            self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
