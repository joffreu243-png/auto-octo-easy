"""
Custom status bar widget for OctoMaster Pro.

Provides status information with indicators for workflow state, recording, etc.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QProgressBar


class CustomStatusBar(QStatusBar):
    """Custom status bar with indicators."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize status bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup status bar UI."""
        # Main message label
        self._message_label = QLabel("Ready")
        self.addWidget(self._message_label, 1)

        # Workflow status indicator
        self._workflow_status = QLabel("⚫ Idle")
        self._workflow_status.setToolTip("Workflow Status")
        self.addPermanentWidget(self._workflow_status)

        # Recording indicator
        self._recording_status = QLabel()
        self._recording_status.setVisible(False)
        self._recording_status.setToolTip("Recording Active")
        self.addPermanentWidget(self._recording_status)

        # Recording blink timer
        self._blink_timer = QTimer()
        self._blink_timer.timeout.connect(self._blink_recording)
        self._blink_state = False

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setTextVisible(True)
        self.addPermanentWidget(self._progress_bar)

        # Project info
        self._project_label = QLabel("No project")
        self._project_label.setToolTip("Current Project")
        self.addPermanentWidget(self._project_label)

        # Stats
        self._stats_label = QLabel("0 nodes")
        self._stats_label.setToolTip("Workflow Statistics")
        self.addPermanentWidget(self._stats_label)

    def show_message(
        self, message: str, timeout: int = 0, priority: str = "info"
    ) -> None:
        """Show temporary message in status bar.

        Args:
            message: Message to display
            timeout: Time to show message (ms), 0 = permanent
            priority: Message priority (info, warning, error, success)
        """
        # Add icon based on priority
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
        }
        icon = icons.get(priority, "")
        full_message = f"{icon} {message}" if icon else message

        if timeout > 0:
            self.showMessage(full_message, timeout)
        else:
            self._message_label.setText(full_message)

    def set_workflow_status(self, status: str, running: bool = False) -> None:
        """Set workflow status indicator.

        Args:
            status: Status text
            running: Whether workflow is currently running
        """
        if running:
            self._workflow_status.setText(f"🟢 {status}")
        else:
            self._workflow_status.setText(f"⚫ {status}")

    def set_recording(self, recording: bool) -> None:
        """Set recording status.

        Args:
            recording: Whether recording is active
        """
        if recording:
            self._recording_status.setText("⏺️ Recording")
            self._recording_status.setVisible(True)
            self._blink_timer.start(500)  # Blink every 500ms
        else:
            self._recording_status.setVisible(False)
            self._blink_timer.stop()

    def _blink_recording(self) -> None:
        """Blink recording indicator."""
        self._blink_state = not self._blink_state
        if self._blink_state:
            self._recording_status.setText("⏺️ Recording")
        else:
            self._recording_status.setText("⚪ Recording")

    def show_progress(
        self, visible: bool, value: int = 0, maximum: int = 100, text: str = ""
    ) -> None:
        """Show/hide progress bar.

        Args:
            visible: Whether to show progress bar
            value: Current progress value
            maximum: Maximum progress value
            text: Progress text
        """
        self._progress_bar.setVisible(visible)
        if visible:
            self._progress_bar.setMaximum(maximum)
            self._progress_bar.setValue(value)
            if text:
                self._progress_bar.setFormat(text)

    def update_progress(self, value: int, text: str = "") -> None:
        """Update progress bar value.

        Args:
            value: New progress value
            text: Optional progress text
        """
        self._progress_bar.setValue(value)
        if text:
            self._progress_bar.setFormat(text)

    def set_project_info(self, project_name: str) -> None:
        """Set current project information.

        Args:
            project_name: Name of current project
        """
        if project_name:
            self._project_label.setText(f"📁 {project_name}")
        else:
            self._project_label.setText("No project")

    def update_stats(self, node_count: int, connection_count: int = 0) -> None:
        """Update workflow statistics.

        Args:
            node_count: Number of nodes in workflow
            connection_count: Number of connections
        """
        if connection_count > 0:
            self._stats_label.setText(
                f"{node_count} nodes, {connection_count} connections"
            )
        else:
            self._stats_label.setText(f"{node_count} nodes")

    def clear_message(self) -> None:
        """Clear status message."""
        self._message_label.setText("Ready")
