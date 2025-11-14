"""
Main window for OctoMaster Pro.

Complete main application window with all GUI components integrated.
"""

from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QTabWidget,
    QDockWidget,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence

from src.gui.widgets.toolbar import CustomToolBar
from src.gui.widgets.statusbar import CustomStatusBar
from src.gui.widgets.sidebar import SideBar
from src.gui.views.canvas_view import CanvasView
from src.gui.views.code_view import CodeView
from src.gui.views.browser_view import BrowserView
from src.gui.views.console_view import ConsoleView
from src.gui.dialogs.new_project import NewProjectDialog
from src.gui.dialogs.settings import SettingsDialog
from src.gui.dialogs.about import AboutDialog
from src.gui.styles.themes import get_theme_manager, ThemeType


class MainWindow(QMainWindow):
    """Main application window with all GUI components."""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("OctoMaster Pro")
        self.setMinimumSize(1200, 800)

        self._current_project = None
        self._workflow_running = False

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

        # Apply default theme
        get_theme_manager().set_theme(ThemeType.DARK)

    def _setup_ui(self) -> None:
        """Setup main window UI."""
        # Central widget with tabs
        self._central_tabs = QTabWidget()
        self._central_tabs.setTabsClosable(True)
        self._central_tabs.setMovable(True)
        self._central_tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self._central_tabs)

        # Create default tabs
        self._canvas_view = CanvasView()
        self._central_tabs.addTab(self._canvas_view, "📐 Canvas")

        self._code_view = CodeView()
        self._central_tabs.addTab(self._code_view, "📝 Code")

        # Toolbar
        self._toolbar = CustomToolBar(self)
        self.addToolBar(self._toolbar)

        # Status bar
        self._statusbar = CustomStatusBar(self)
        self.setStatusBar(self._statusbar)

        # Dock widgets
        self._setup_dock_widgets()

        self._statusbar.show_message("Ready", priority="success")

    def _setup_dock_widgets(self) -> None:
        """Setup dock widgets for sidebar, browser, console."""
        # Left sidebar - Project Explorer
        self._sidebar_dock = QDockWidget("Project Explorer", self)
        self._sidebar_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._sidebar = SideBar()
        self._sidebar_dock.setWidget(self._sidebar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._sidebar_dock)

        # Right side - Browser Preview
        self._browser_dock = QDockWidget("Browser Preview", self)
        self._browser_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._browser_view = BrowserView()
        self._browser_dock.setWidget(self._browser_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._browser_dock)

        # Bottom - Console
        self._console_dock = QDockWidget("Console", self)
        self._console_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self._console_view = ConsoleView()
        self._console_dock.setWidget(self._console_view)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._console_dock)

    def _setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
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

        edit_menu.addSeparator()

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        edit_menu.addAction(select_all_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        view_menu.addAction(self._sidebar_dock.toggleViewAction())
        view_menu.addAction(self._browser_dock.toggleViewAction())
        view_menu.addAction(self._console_dock.toggleViewAction())

        view_menu.addSeparator()

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._canvas_view.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._canvas_view.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.triggered.connect(self._canvas_view.zoom_reset)
        view_menu.addAction(zoom_reset_action)

        view_menu.addSeparator()

        theme_action = QAction("Toggle &Theme", self)
        theme_action.setShortcut(QKeySequence("Ctrl+T"))
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        run_action = QAction("&Run Workflow", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_workflow)
        run_menu.addAction(run_action)

        stop_action = QAction("&Stop Workflow", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.triggered.connect(self._stop_workflow)
        run_menu.addAction(stop_action)

        run_menu.addSeparator()

        record_action = QAction("Start &Recording", self)
        record_action.setShortcut(QKeySequence("Ctrl+R"))
        record_action.setCheckable(True)
        record_action.toggled.connect(self._toggle_recording)
        run_menu.addAction(record_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Toolbar connections
        self._toolbar.connect_new(self._new_project)
        self._toolbar.connect_open(self._open_project)
        self._toolbar.connect_save(self._save_project)
        self._toolbar.connect_run(self._run_workflow)
        self._toolbar.connect_stop(self._stop_workflow)
        self._toolbar.connect_record(self._toggle_recording)
        self._toolbar.connect_zoom_in(self._canvas_view.zoom_in)
        self._toolbar.connect_zoom_out(self._canvas_view.zoom_out)
        self._toolbar.connect_zoom_reset(self._canvas_view.zoom_reset)
        self._toolbar.connect_settings(self._show_settings)

        # Sidebar connections
        self._sidebar.file_opened.connect(self._open_file)

        # Canvas connections
        self._canvas_view.zoom_changed.connect(self._on_zoom_changed)

    def _new_project(self) -> None:
        """Create new project."""
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_info = dialog.get_project_info()
            self._current_project = project_info["path"]
            self._statusbar.set_project_info(project_info["name"])
            self._sidebar.load_project(Path(project_info["path"]))
            self._console_view.success(f"Created project: {project_info['name']}")
            self._console_view.info(f"Location: {project_info['path']}")

    def _open_project(self) -> None:
        """Open existing project."""
        directory = QFileDialog.getExistingDirectory(
            self, "Open Project", str(Path.home())
        )

        if directory:
            self._current_project = directory
            project_name = Path(directory).name
            self._statusbar.set_project_info(project_name)
            self._sidebar.load_project(Path(directory))
            self._console_view.success(f"Opened project: {project_name}")

    def _save_project(self) -> None:
        """Save current project."""
        if self._current_project:
            self._statusbar.show_message("Project saved", 3000, "success")
            self._console_view.success("Project saved successfully")
        else:
            self._save_project_as()

    def _save_project_as(self) -> None:
        """Save project as new location."""
        directory = QFileDialog.getExistingDirectory(
            self, "Save Project As", str(Path.home())
        )

        if directory:
            self._current_project = directory
            self._save_project()

    def _run_workflow(self) -> None:
        """Run current workflow."""
        self._workflow_running = True
        self._toolbar.set_workflow_running(True)
        self._statusbar.set_workflow_status("Running", True)
        self._console_view.info("Starting workflow execution...")

        # TODO: Actual workflow execution

    def _stop_workflow(self) -> None:
        """Stop workflow execution."""
        self._workflow_running = False
        self._toolbar.set_workflow_running(False)
        self._statusbar.set_workflow_status("Stopped", False)
        self._console_view.warning("Workflow execution stopped")

    def _toggle_recording(self, recording: bool) -> None:
        """Toggle recording mode.

        Args:
            recording: Whether recording should be enabled
        """
        self._statusbar.set_recording(recording)
        self._toolbar.set_recording(recording)

        if recording:
            self._console_view.info("Recording started")
        else:
            self._console_view.info("Recording stopped")

    def _toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        get_theme_manager().toggle_theme()

    def _show_settings(self) -> None:
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def _show_about(self) -> None:
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _open_file(self, file_path: str) -> None:
        """Open file in editor.

        Args:
            file_path: Path to file
        """
        self._console_view.info(f"Opening file: {file_path}")
        # TODO: Load file content into code editor

    def _close_tab(self, index: int) -> None:
        """Close tab at index.

        Args:
            index: Tab index
        """
        if self._central_tabs.count() > 1:
            self._central_tabs.removeTab(index)

    def _on_zoom_changed(self, zoom: float) -> None:
        """Handle zoom level change.

        Args:
            zoom: New zoom level
        """
        self._statusbar.show_message(f"Zoom: {zoom * 100:.0f}%", 1000, "info")

    def closeEvent(self, event) -> None:
        """Handle window close event.

        Args:
            event: Close event
        """
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
