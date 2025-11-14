"""
Custom toolbar widget for OctoMaster Pro.

Provides a toolbar with action buttons, shortcuts, and tooltips.
"""

from typing import Optional, Callable

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtWidgets import QToolBar, QWidget


class CustomToolBar(QToolBar):
    """Custom toolbar with predefined actions."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize toolbar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._setup_actions()

    def _setup_actions(self) -> None:
        """Setup toolbar actions."""
        # File actions
        self.new_action = self._create_action(
            "New Project",
            "Ctrl+N",
            "Create new project",
            "📄",
        )

        self.open_action = self._create_action(
            "Open Project",
            "Ctrl+O",
            "Open existing project",
            "📂",
        )

        self.save_action = self._create_action(
            "Save",
            "Ctrl+S",
            "Save current project",
            "💾",
        )

        self.addSeparator()

        # Edit actions
        self.undo_action = self._create_action(
            "Undo",
            "Ctrl+Z",
            "Undo last action",
            "↶",
        )

        self.redo_action = self._create_action(
            "Redo",
            "Ctrl+Y",
            "Redo last undone action",
            "↷",
        )

        self.addSeparator()

        # Workflow actions
        self.run_action = self._create_action(
            "Run",
            "F5",
            "Run current workflow",
            "▶️",
        )

        self.stop_action = self._create_action(
            "Stop",
            "Shift+F5",
            "Stop workflow execution",
            "⏹️",
        )

        self.record_action = self._create_action(
            "Record",
            "Ctrl+R",
            "Start/Stop recording actions",
            "⏺️",
            checkable=True,
        )

        self.addSeparator()

        # View actions
        self.zoom_in_action = self._create_action(
            "Zoom In",
            "Ctrl++",
            "Zoom in canvas",
            "🔍+",
        )

        self.zoom_out_action = self._create_action(
            "Zoom Out",
            "Ctrl+-",
            "Zoom out canvas",
            "🔍-",
        )

        self.zoom_reset_action = self._create_action(
            "Reset Zoom",
            "Ctrl+0",
            "Reset canvas zoom",
            "🔍",
        )

        self.addSeparator()

        # Settings
        self.settings_action = self._create_action(
            "Settings",
            "Ctrl+,",
            "Open settings",
            "⚙️",
        )

        # Initially disable some actions
        self.stop_action.setEnabled(False)
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)

    def _create_action(
        self,
        text: str,
        shortcut: str,
        tooltip: str,
        icon_text: str = "",
        checkable: bool = False,
    ) -> QAction:
        """Create toolbar action.

        Args:
            text: Action text
            shortcut: Keyboard shortcut
            tooltip: Tooltip text
            icon_text: Icon text (emoji or char)
            checkable: Whether action is checkable

        Returns:
            Created action
        """
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.setToolTip(f"{tooltip} ({shortcut})")
        action.setCheckable(checkable)

        # Use text as icon for now (can be replaced with real icons later)
        if icon_text:
            action.setText(icon_text)

        self.addAction(action)
        return action

    def connect_new(self, callback: Callable) -> None:
        """Connect new project action.

        Args:
            callback: Function to call
        """
        self.new_action.triggered.connect(callback)

    def connect_open(self, callback: Callable) -> None:
        """Connect open project action.

        Args:
            callback: Function to call
        """
        self.open_action.triggered.connect(callback)

    def connect_save(self, callback: Callable) -> None:
        """Connect save action.

        Args:
            callback: Function to call
        """
        self.save_action.triggered.connect(callback)

    def connect_undo(self, callback: Callable) -> None:
        """Connect undo action.

        Args:
            callback: Function to call
        """
        self.undo_action.triggered.connect(callback)

    def connect_redo(self, callback: Callable) -> None:
        """Connect redo action.

        Args:
            callback: Function to call
        """
        self.redo_action.triggered.connect(callback)

    def connect_run(self, callback: Callable) -> None:
        """Connect run action.

        Args:
            callback: Function to call
        """
        self.run_action.triggered.connect(callback)

    def connect_stop(self, callback: Callable) -> None:
        """Connect stop action.

        Args:
            callback: Function to call
        """
        self.stop_action.triggered.connect(callback)

    def connect_record(self, callback: Callable) -> None:
        """Connect record action.

        Args:
            callback: Function to call with bool parameter
        """
        self.record_action.toggled.connect(callback)

    def connect_zoom_in(self, callback: Callable) -> None:
        """Connect zoom in action.

        Args:
            callback: Function to call
        """
        self.zoom_in_action.triggered.connect(callback)

    def connect_zoom_out(self, callback: Callable) -> None:
        """Connect zoom out action.

        Args:
            callback: Function to call
        """
        self.zoom_out_action.triggered.connect(callback)

    def connect_zoom_reset(self, callback: Callable) -> None:
        """Connect zoom reset action.

        Args:
            callback: Function to call
        """
        self.zoom_reset_action.triggered.connect(callback)

    def connect_settings(self, callback: Callable) -> None:
        """Connect settings action.

        Args:
            callback: Function to call
        """
        self.settings_action.triggered.connect(callback)

    def set_workflow_running(self, running: bool) -> None:
        """Update toolbar state for workflow execution.

        Args:
            running: Whether workflow is running
        """
        self.run_action.setEnabled(not running)
        self.stop_action.setEnabled(running)
        self.record_action.setEnabled(not running)
        self.new_action.setEnabled(not running)
        self.open_action.setEnabled(not running)

    def set_recording(self, recording: bool) -> None:
        """Update toolbar state for recording.

        Args:
            recording: Whether recording is active
        """
        self.record_action.setChecked(recording)
        if recording:
            self.record_action.setToolTip("Stop Recording (Ctrl+R)")
        else:
            self.record_action.setToolTip("Start Recording (Ctrl+R)")

    def enable_undo(self, enabled: bool) -> None:
        """Enable/disable undo action.

        Args:
            enabled: Whether to enable undo
        """
        self.undo_action.setEnabled(enabled)

    def enable_redo(self, enabled: bool) -> None:
        """Enable/disable redo action.

        Args:
            enabled: Whether to enable redo
        """
        self.redo_action.setEnabled(enabled)
