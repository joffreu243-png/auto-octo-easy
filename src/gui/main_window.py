"""
Main window for OctoMaster Pro.

This module provides the main application window with visual workflow editor,
browser panel, control panels, and menu system.
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QMenuBar,
    QMenu,
    QToolBar,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QDockWidget,
    QTabWidget,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from loguru import logger

from src.core.config import get_config
from src.core.state import get_app_state
from src.core.events import get_event_bus, EventType
from src.core.exceptions import OctoMasterError


class MainWindow(QMainWindow):
    """
    Main application window.

    Provides the primary user interface with workflow editor, browser panel,
    controls, and menu system.
    """

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()

        self.config = get_config()
        self.state = get_app_state()
        self.event_bus = get_event_bus()

        # Current workflow path
        self.current_workflow_path: Optional[Path] = None

        # Initialize UI
        self.setup_ui()
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_shortcuts()
        self.setup_connections()

        logger.info("Main window initialized")

    def setup_ui(self) -> None:
        """Setup the main UI layout."""
        self.setWindowTitle("OctoMaster Pro - Visual Browser Automation")
        self.setGeometry(100, 100, 1600, 900)

        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter (vertical)
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section: Visual Editor
        self.editor_widget = self._create_editor_widget()
        main_splitter.addWidget(self.editor_widget)

        # Bottom section: Browser and Console tabs
        self.bottom_tabs = self._create_bottom_tabs()
        main_splitter.addWidget(self.bottom_tabs)

        # Set initial sizes (70% editor, 30% bottom)
        main_splitter.setSizes([700, 300])

        layout.addWidget(main_splitter)

        # Create dock widgets for side panels
        self._create_dock_widgets()

        logger.debug("UI layout created")

    def _create_editor_widget(self) -> QWidget:
        """
        Create the visual workflow editor widget.

        Returns:
            Editor widget
        """
        # TODO: Import and create actual VisualEditor
        editor = QWidget()
        editor_layout = QVBoxLayout(editor)

        # Placeholder for visual editor
        from PyQt6.QtWidgets import QLabel
        placeholder = QLabel("Visual Workflow Editor\n\nDrag and drop blocks to create workflows")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("background-color: #f5f5f5; border: 2px dashed #ccc; font-size: 16px;")

        editor_layout.addWidget(placeholder)

        return editor

    def _create_bottom_tabs(self) -> QTabWidget:
        """
        Create bottom tabbed panel with browser, console, logs, etc.

        Returns:
            Tab widget
        """
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.South)
        tabs.setMaximumHeight(350)

        # Browser tab
        self.browser_widget = self._create_browser_widget()
        tabs.addTab(self.browser_widget, "🌐 Browser")

        # Console tab
        self.console_widget = self._create_console_widget()
        tabs.addTab(self.console_widget, "📟 Console")

        # Logs tab
        self.logs_widget = self._create_logs_widget()
        tabs.addTab(self.logs_widget, "📋 Logs")

        # Variables tab
        self.variables_widget = self._create_variables_widget()
        tabs.addTab(self.variables_widget, "🔤 Variables")

        # Debugger tab
        self.debugger_widget = self._create_debugger_widget()
        tabs.addTab(self.debugger_widget, "🐞 Debugger")

        return tabs

    def _create_browser_widget(self) -> QWidget:
        """Create browser widget."""
        # TODO: Import actual BrowserPanel
        from PyQt6.QtWidgets import QLabel
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Browser Preview Panel\n\nBrowser will be shown here during execution")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def _create_console_widget(self) -> QWidget:
        """Create console widget."""
        from PyQt6.QtWidgets import QTextEdit
        console = QTextEdit()
        console.setReadOnly(True)
        console.setPlaceholderText("Console output will appear here...")
        return console

    def _create_logs_widget(self) -> QWidget:
        """Create logs widget."""
        # TODO: Import actual LogsWidget
        from PyQt6.QtWidgets import QTextEdit
        logs = QTextEdit()
        logs.setReadOnly(True)
        logs.setPlaceholderText("Application logs will appear here...")
        return logs

    def _create_variables_widget(self) -> QWidget:
        """Create variables widget."""
        # TODO: Import actual VariablesWidget
        from PyQt6.QtWidgets import QLabel
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Variables Panel\n\nWorkflow variables will be shown here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def _create_debugger_widget(self) -> QWidget:
        """Create debugger widget."""
        # TODO: Import actual DebuggerWidget
        from PyQt6.QtWidgets import QLabel
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Debugger Panel\n\nBreakpoints and debugging tools")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def _create_dock_widgets(self) -> None:
        """Create dockable widgets for side panels."""
        # Blocks Library (left)
        self.blocks_dock = QDockWidget("Blocks Library", self)
        self.blocks_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        from PyQt6.QtWidgets import QListWidget
        blocks_list = QListWidget()
        blocks_list.addItems(["Navigate", "Click", "Type", "Wait", "Extract Data", "Condition"])
        self.blocks_dock.setWidget(blocks_list)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.blocks_dock)

        # Properties panel (right)
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        from PyQt6.QtWidgets import QLabel
        properties_widget = QLabel("Properties panel\n\nSelect a block to edit")
        properties_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.properties_dock.setWidget(properties_widget)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

    def setup_menubar(self) -> None:
        """Setup the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        self.new_action = QAction("&New Workflow", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(self.new_action)

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(self.open_action)

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.save_workflow_as)
        file_menu.addAction(self.save_as_action)

        file_menu.addSeparator()

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("&Undo").setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction("&Redo").setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Cu&t").setShortcut(QKeySequence.StandardKey.Cut)
        edit_menu.addAction("&Copy").setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction("&Paste").setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction("&Delete").setShortcut(QKeySequence.StandardKey.Delete)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.blocks_dock.toggleViewAction())
        view_menu.addAction(self.properties_dock.toggleViewAction())
        view_menu.addSeparator()
        view_menu.addAction("Zoom &In").setShortcut(QKeySequence.StandardKey.ZoomIn)
        view_menu.addAction("Zoom &Out").setShortcut(QKeySequence.StandardKey.ZoomOut)
        view_menu.addAction("&Reset Zoom").setShortcut(QKeySequence("Ctrl+0"))

        # Run menu
        run_menu = menubar.addMenu("&Run")

        self.run_action = QAction("▶ &Run Workflow", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.triggered.connect(self.run_workflow)
        run_menu.addAction(self.run_action)

        self.debug_action = QAction("🐞 &Debug Workflow", self)
        self.debug_action.setShortcut(QKeySequence("F8"))
        run_menu.addAction(self.debug_action)

        self.stop_action = QAction("⏹ &Stop", self)
        self.stop_action.setShortcut(QKeySequence("Shift+F5"))
        self.stop_action.setEnabled(False)
        run_menu.addAction(self.stop_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        self.recorder_action = QAction("🔴 &Recorder", self)
        self.recorder_action.setShortcut(QKeySequence("Ctrl+R"))
        tools_menu.addAction(self.recorder_action)

        tools_menu.addSeparator()
        tools_menu.addAction("&Settings...").setShortcut(QKeySequence.StandardKey.Preferences)
        tools_menu.addAction("&Plugins...")

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&Quick Start").setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction("&Documentation")
        help_menu.addSeparator()
        help_menu.addAction("&About")

    def setup_toolbar(self) -> None:
        """Setup the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # File actions
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)

        toolbar.addSeparator()

        # Run actions
        toolbar.addAction(self.run_action)
        toolbar.addAction(self.stop_action)

        toolbar.addSeparator()

        # Tools
        toolbar.addAction(self.recorder_action)

    def setup_statusbar(self) -> None:
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Additional shortcuts beyond menu items
        pass

    def setup_connections(self) -> None:
        """Setup signal/slot connections."""
        # Subscribe to events
        self.event_bus.subscribe(EventType.WORKFLOW_STARTED, self.on_workflow_started)
        self.event_bus.subscribe(EventType.WORKFLOW_COMPLETED, self.on_workflow_completed)
        self.event_bus.subscribe(EventType.WORKFLOW_FAILED, self.on_workflow_failed)

    # Slots and handlers

    @pyqtSlot()
    def new_workflow(self) -> None:
        """Create a new workflow."""
        logger.info("Creating new workflow")
        self.current_workflow_path = None
        self.setWindowTitle("OctoMaster Pro - Untitled")
        self.status_bar.showMessage("New workflow created")

    @pyqtSlot()
    def open_workflow(self) -> None:
        """Open an existing workflow."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Workflow",
            str(self.config.data_dir or Path.home()),
            "Workflow Files (*.json *.yaml);;All Files (*)",
        )

        if file_path:
            logger.info(f"Opening workflow: {file_path}")
            self.current_workflow_path = Path(file_path)
            self.setWindowTitle(f"OctoMaster Pro - {Path(file_path).name}")
            self.status_bar.showMessage(f"Opened {Path(file_path).name}")

    @pyqtSlot()
    def save_workflow(self) -> None:
        """Save the current workflow."""
        if self.current_workflow_path:
            logger.info(f"Saving workflow: {self.current_workflow_path}")
            self.status_bar.showMessage(f"Saved {self.current_workflow_path.name}")
        else:
            self.save_workflow_as()

    @pyqtSlot()
    def save_workflow_as(self) -> None:
        """Save the workflow with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Workflow As",
            str(self.config.data_dir or Path.home()),
            "JSON Files (*.json);;YAML Files (*.yaml);;All Files (*)",
        )

        if file_path:
            logger.info(f"Saving workflow as: {file_path}")
            self.current_workflow_path = Path(file_path)
            self.setWindowTitle(f"OctoMaster Pro - {Path(file_path).name}")
            self.status_bar.showMessage(f"Saved as {Path(file_path).name}")

    @pyqtSlot()
    def run_workflow(self) -> None:
        """Run the current workflow."""
        logger.info("Running workflow")
        self.status_bar.showMessage("Running workflow...")

        self.run_action.setEnabled(False)
        self.stop_action.setEnabled(True)

        # TODO: Actually execute the workflow
        # Simulate execution for now
        QTimer.singleShot(2000, self.on_workflow_completed)

    def on_workflow_started(self, event) -> None:
        """Handle workflow started event."""
        logger.info("Workflow started")

    def on_workflow_completed(self, event=None) -> None:
        """Handle workflow completed event."""
        logger.info("Workflow completed")
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.status_bar.showMessage("Workflow completed successfully")

    def on_workflow_failed(self, event) -> None:
        """Handle workflow failed event."""
        logger.error("Workflow failed")
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.status_bar.showMessage("Workflow failed")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Check for unsaved changes
        # TODO: Implement unsaved changes check

        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Main window closing")
            event.accept()
        else:
            event.ignore()
