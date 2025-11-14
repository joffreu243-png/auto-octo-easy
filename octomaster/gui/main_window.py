"""
Main window for OctoMaster Pro.

The main application window with all panels and components.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QToolBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from loguru import logger

from octomaster.core.config import Config
from octomaster.core.workflow import Workflow
from octomaster.gui.widgets.project_explorer import ProjectExplorer
from octomaster.gui.widgets.visual_editor import VisualEditor
from octomaster.gui.widgets.inspector_panel import InspectorPanel
from octomaster.gui.widgets.console_widget import ConsoleWidget
from octomaster.gui.widgets.browser_panel import BrowserPanel


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    workflow_changed = pyqtSignal(Workflow)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.current_workflow: Workflow = Workflow()
        self.is_recording = False

        self.setWindowTitle(f"{config.app_name} v{config.app_version}")
        self.setGeometry(100, 100, 1600, 900)

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        logger.info("Main window initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Project Explorer
        self.project_explorer = ProjectExplorer(self)
        main_splitter.addWidget(self.project_explorer)

        # Center panel - Visual Editor
        self.visual_editor = VisualEditor(self)
        main_splitter.addWidget(self.visual_editor)

        # Right panel - Inspector
        self.inspector_panel = InspectorPanel(self)
        main_splitter.addWidget(self.inspector_panel)

        # Set splitter sizes (20% - 60% - 20%)
        main_splitter.setSizes([300, 900, 300])

        # Bottom panel - Tabs
        bottom_panel = QTabWidget()
        bottom_panel.setMaximumHeight(250)

        # Console tab
        self.console_widget = ConsoleWidget(self)
        bottom_panel.addTab(self.console_widget, "Console")

        # Browser tab
        self.browser_panel = BrowserPanel(self)
        bottom_panel.addTab(self.browser_panel, "Browser")

        # Logs tab
        # TODO: Implement logs widget
        bottom_panel.addTab(QWidget(), "Logs")

        # Variables tab
        # TODO: Implement variables widget
        bottom_panel.addTab(QWidget(), "Variables")

        # Debugger tab
        # TODO: Implement debugger widget
        bottom_panel.addTab(QWidget(), "Debugger")

        # Vertical splitter for main content and bottom panel
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.addWidget(main_splitter)
        vertical_splitter.addWidget(bottom_panel)
        vertical_splitter.setSizes([650, 250])

        main_layout.addWidget(vertical_splitter)

    def _setup_menus(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        # New
        new_action = QAction("&New Workflow", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(new_action)

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(open_action)

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(save_action)

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_workflow_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Export
        export_menu = file_menu.addMenu("Export")
        export_python_action = QAction("Export as Python...", self)
        export_python_action.triggered.connect(self.export_as_python)
        export_menu.addAction(export_python_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)

        # View Menu
        view_menu = menubar.addMenu("&View")
        # TODO: Add view options

        # Run Menu
        run_menu = menubar.addMenu("&Run")

        run_action = QAction("&Run Workflow", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self.run_workflow)
        run_menu.addAction(run_action)

        debug_action = QAction("&Debug Workflow", self)
        debug_action.setShortcut(QKeySequence("F8"))
        run_menu.addAction(debug_action)

        run_menu.addSeparator()

        stop_action = QAction("&Stop", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        run_menu.addAction(stop_action)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        tools_menu.addAction(settings_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction(docs_action)

    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # New
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_workflow)
        toolbar.addAction(new_action)

        # Open
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_workflow)
        toolbar.addAction(open_action)

        # Save
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_workflow)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Run
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_workflow)
        toolbar.addAction(run_action)

        # Pause
        pause_action = QAction("Pause", self)
        toolbar.addAction(pause_action)

        # Stop
        stop_action = QAction("Stop", self)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Record
        self.record_action = QAction("🔴 Record", self)
        self.record_action.setCheckable(True)
        self.record_action.triggered.connect(self.toggle_recording)
        toolbar.addAction(self.record_action)

        toolbar.addSeparator()

        # Debug
        debug_action = QAction("Debug", self)
        toolbar.addAction(debug_action)

        # Screenshot
        screenshot_action = QAction("Screenshot", self)
        toolbar.addAction(screenshot_action)

        toolbar.addSeparator()

        # Settings
        settings_action = QAction("Settings", self)
        toolbar.addAction(settings_action)

    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusBar().showMessage("Ready")

    def _connect_signals(self):
        """Connect signals and slots."""
        self.visual_editor.workflow_changed.connect(self.on_workflow_changed)

    # Slots
    def new_workflow(self):
        """Create a new workflow."""
        # TODO: Check if current workflow needs saving
        self.current_workflow = Workflow()
        self.visual_editor.set_workflow(self.current_workflow)
        self.statusBar().showMessage("New workflow created")
        logger.info("New workflow created")

    def open_workflow(self):
        """Open an existing workflow."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Workflow", str(self.config.projects_dir), "Workflow Files (*.workflow *.json)"
        )

        if file_path:
            try:
                from pathlib import Path

                workflow = Workflow.load(Path(file_path))
                self.current_workflow = workflow
                self.visual_editor.set_workflow(workflow)
                self.statusBar().showMessage(f"Opened: {file_path}")
                logger.info(f"Workflow loaded from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load workflow: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load workflow:\n{e}")

    def save_workflow(self):
        """Save the current workflow."""
        # TODO: Implement proper save logic
        self.statusBar().showMessage("Workflow saved")
        logger.info("Workflow saved")

    def save_workflow_as(self):
        """Save workflow with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Workflow As", str(self.config.projects_dir), "Workflow Files (*.workflow)"
        )

        if file_path:
            try:
                from pathlib import Path

                self.current_workflow.save(Path(file_path))
                self.statusBar().showMessage(f"Saved: {file_path}")
                logger.info(f"Workflow saved to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save workflow: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save workflow:\n{e}")

    def export_as_python(self):
        """Export workflow as Python code."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as Python", str(self.config.projects_dir), "Python Files (*.py)"
        )

        if file_path:
            try:
                code = self.current_workflow.export_to_python()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.statusBar().showMessage(f"Exported to: {file_path}")
                logger.info(f"Workflow exported to {file_path}")
                QMessageBox.information(
                    self, "Export Successful", f"Workflow exported to:\n{file_path}"
                )
            except Exception as e:
                logger.error(f"Failed to export workflow: {e}")
                QMessageBox.critical(self, "Error", f"Failed to export workflow:\n{e}")

    def run_workflow(self):
        """Run the current workflow."""
        logger.info("Running workflow...")
        self.statusBar().showMessage("Running workflow...")
        # TODO: Implement workflow execution
        self.console_widget.append_text("Running workflow...\n")

    def toggle_recording(self, checked: bool):
        """Toggle action recording."""
        if checked:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording actions."""
        self.is_recording = True
        self.record_action.setText("⏹️ Stop Recording")
        self.statusBar().showMessage("🔴 Recording...")
        self.recording_started.emit()
        logger.info("Recording started")

    def stop_recording(self):
        """Stop recording actions."""
        self.is_recording = False
        self.record_action.setText("🔴 Record")
        self.record_action.setChecked(False)
        self.statusBar().showMessage("Recording stopped")
        self.recording_stopped.emit()
        logger.info("Recording stopped")

    def on_workflow_changed(self, workflow: Workflow):
        """Handle workflow changes."""
        self.current_workflow = workflow
        self.workflow_changed.emit(workflow)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {self.config.app_name}",
            f"""
            <h2>{self.config.app_name}</h2>
            <p>Version: {self.config.app_version}</p>
            <p>Revolutionary browser automation platform with visual workflow builder</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Visual node-based workflow builder</li>
                <li>Action recorder</li>
                <li>AI assistant</li>
                <li>Octo Browser integration</li>
                <li>Template library</li>
            </ul>
            <p>© 2025 OctoMaster Team</p>
            """,
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # TODO: Check if workflow needs saving
        logger.info("Application closing...")
        event.accept()
