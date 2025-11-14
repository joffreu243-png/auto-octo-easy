"""
Debugger Widget for OctoMaster Pro.

Provides debugging capabilities for workflow execution.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QSplitter,
    QTextEdit,
    QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from loguru import logger


class DebuggerWidget(QWidget):
    """Widget for debugging workflow execution."""

    # Signals
    breakpoint_added = pyqtSignal(str)  # block_id
    breakpoint_removed = pyqtSignal(str)  # block_id
    step_requested = pyqtSignal()
    continue_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.breakpoints = set()
        self.current_block = None
        self.execution_stack = []
        self.is_debugging = False
        self.is_paused = False
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Control toolbar
        toolbar = QHBoxLayout()

        # Debug controls
        self.start_debug_btn = QPushButton("▶ Start Debug")
        self.start_debug_btn.clicked.connect(self.start_debugging)
        toolbar.addWidget(self.start_debug_btn)

        self.step_btn = QPushButton("→ Step")
        self.step_btn.setEnabled(False)
        self.step_btn.clicked.connect(self.step_requested.emit)
        toolbar.addWidget(self.step_btn)

        self.continue_btn = QPushButton("⏭ Continue")
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.continue_requested.emit)
        toolbar.addWidget(self.continue_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        toolbar.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        toolbar.addWidget(self.stop_btn)

        toolbar.addStretch()

        # Auto-pause on error
        self.auto_pause_error = QCheckBox("Pause on Error")
        self.auto_pause_error.setChecked(True)
        toolbar.addWidget(self.auto_pause_error)

        layout.addLayout(toolbar)

        # Splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Breakpoints panel
        breakpoints_panel = QWidget()
        breakpoints_layout = QVBoxLayout(breakpoints_panel)
        breakpoints_layout.setContentsMargins(0, 0, 0, 0)

        # Breakpoints header
        bp_header = QHBoxLayout()
        bp_header.addWidget(QLabel("<b>Breakpoints</b>"))
        bp_header.addStretch()

        clear_bp_btn = QPushButton("Clear All")
        clear_bp_btn.clicked.connect(self.clear_breakpoints)
        bp_header.addWidget(clear_bp_btn)

        breakpoints_layout.addLayout(bp_header)

        # Breakpoints table
        self.breakpoints_table = QTableWidget()
        self.breakpoints_table.setColumnCount(3)
        self.breakpoints_table.setHorizontalHeaderLabels(["Block", "Type", "Enabled"])
        self.breakpoints_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.breakpoints_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.breakpoints_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.breakpoints_table.setMaximumHeight(150)
        breakpoints_layout.addWidget(self.breakpoints_table)

        splitter.addWidget(breakpoints_panel)

        # Call stack panel
        stack_panel = QWidget()
        stack_layout = QVBoxLayout(stack_panel)
        stack_layout.setContentsMargins(0, 0, 0, 0)

        stack_layout.addWidget(QLabel("<b>Call Stack</b>"))

        self.stack_table = QTableWidget()
        self.stack_table.setColumnCount(2)
        self.stack_table.setHorizontalHeaderLabels(["Level", "Block"])
        self.stack_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.stack_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.stack_table.setMaximumHeight(150)
        stack_layout.addWidget(self.stack_table)

        splitter.addWidget(stack_panel)

        # Output panel
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)

        output_layout.addWidget(QLabel("<b>Debug Output</b>"))

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 9))
        output_layout.addWidget(self.output_text)

        splitter.addWidget(output_panel)

        # Set splitter sizes
        splitter.setSizes([150, 150, 200])

        layout.addWidget(splitter)

    def start_debugging(self):
        """Start debugging session."""
        self.is_debugging = True
        self.is_paused = False

        # Update UI
        self.start_debug_btn.setEnabled(False)
        self.step_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.log_debug("Debugging session started")
        logger.info("Debugging started")

    def stop_debugging(self):
        """Stop debugging session."""
        self.is_debugging = False
        self.is_paused = False
        self.current_block = None
        self.execution_stack.clear()

        # Update UI
        self.start_debug_btn.setEnabled(True)
        self.step_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.update_stack_table()
        self.log_debug("Debugging session stopped")
        logger.info("Debugging stopped")

    def pause_debugging(self):
        """Pause debugging session."""
        self.is_paused = True
        self.step_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.log_debug("Execution paused")

    def resume_debugging(self):
        """Resume debugging session."""
        self.is_paused = False
        self.step_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.log_debug("Execution resumed")

    def add_breakpoint(self, block_id: str, block_name: str = "", block_type: str = ""):
        """Add a breakpoint."""
        if block_id not in self.breakpoints:
            self.breakpoints.add(block_id)
            self.refresh_breakpoints_table()
            self.breakpoint_added.emit(block_id)
            logger.debug(f"Breakpoint added: {block_id}")

    def remove_breakpoint(self, block_id: str):
        """Remove a breakpoint."""
        if block_id in self.breakpoints:
            self.breakpoints.remove(block_id)
            self.refresh_breakpoints_table()
            self.breakpoint_removed.emit(block_id)
            logger.debug(f"Breakpoint removed: {block_id}")

    def toggle_breakpoint(self, block_id: str, block_name: str = "", block_type: str = ""):
        """Toggle a breakpoint."""
        if block_id in self.breakpoints:
            self.remove_breakpoint(block_id)
        else:
            self.add_breakpoint(block_id, block_name, block_type)

    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.breakpoints.clear()
        self.refresh_breakpoints_table()
        self.log_debug("All breakpoints cleared")

    def has_breakpoint(self, block_id: str) -> bool:
        """Check if block has breakpoint."""
        return block_id in self.breakpoints

    def set_current_block(self, block_id: str, block_name: str = ""):
        """Set the currently executing block."""
        self.current_block = block_id
        self.log_debug(f"→ Executing: {block_name or block_id}")

    def push_stack(self, block_id: str, block_name: str = ""):
        """Push block onto execution stack."""
        self.execution_stack.append({
            "block_id": block_id,
            "block_name": block_name
        })
        self.update_stack_table()

    def pop_stack(self):
        """Pop block from execution stack."""
        if self.execution_stack:
            self.execution_stack.pop()
            self.update_stack_table()

    def clear_stack(self):
        """Clear execution stack."""
        self.execution_stack.clear()
        self.update_stack_table()

    def log_debug(self, message: str):
        """Log debug message."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.output_text.append(f"[{timestamp}] {message}")

    def log_error(self, message: str):
        """Log error message."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.output_text.append(f'<span style="color: red;">[{timestamp}] ERROR: {message}</span>')

        # Auto-pause on error if enabled
        if self.auto_pause_error.isChecked() and self.is_debugging:
            self.pause_debugging()

    def refresh_breakpoints_table(self):
        """Refresh breakpoints table."""
        self.breakpoints_table.setRowCount(0)

        for block_id in sorted(self.breakpoints):
            row = self.breakpoints_table.rowCount()
            self.breakpoints_table.insertRow(row)

            # Block ID
            self.breakpoints_table.setItem(row, 0, QTableWidgetItem(block_id))

            # Type (placeholder)
            self.breakpoints_table.setItem(row, 1, QTableWidgetItem("Block"))

            # Enabled
            enabled_item = QTableWidgetItem("✓")
            enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            enabled_item.setForeground(QColor("#28a745"))
            self.breakpoints_table.setItem(row, 2, enabled_item)

    def update_stack_table(self):
        """Update call stack table."""
        self.stack_table.setRowCount(0)

        for i, frame in enumerate(reversed(self.execution_stack)):
            row = self.stack_table.rowCount()
            self.stack_table.insertRow(row)

            # Level
            level_item = QTableWidgetItem(str(i))
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack_table.setItem(row, 0, level_item)

            # Block
            block_name = frame.get("block_name") or frame.get("block_id")
            self.stack_table.setItem(row, 1, QTableWidgetItem(block_name))

    def clear_output(self):
        """Clear debug output."""
        self.output_text.clear()
