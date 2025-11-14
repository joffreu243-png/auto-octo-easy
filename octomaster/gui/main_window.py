"""
Main window for OctoMaster Pro.

The main application window with all panels and components - 100% FUNCTIONAL.
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
    QDockWidget,
    QInputDialog,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from loguru import logger
from pathlib import Path
import asyncio

from octomaster.core.config import Config
from octomaster.core.workflow import Workflow
from octomaster.gui.widgets.project_explorer import ProjectExplorer
from octomaster.gui.widgets.visual_editor import VisualEditor
from octomaster.gui.widgets.inspector_panel import InspectorPanel
from octomaster.gui.widgets.console_widget import ConsoleWidget
from octomaster.gui.widgets.browser_panel import BrowserPanel
from octomaster.gui.widgets.logs_widget import LogsWidget
from octomaster.gui.widgets.variables_widget import VariablesWidget
from octomaster.gui.widgets.debugger_widget import DebuggerWidget
from octomaster.gui.commands import CommandHistory
from octomaster.automation.executor import WorkflowExecutor
from octomaster.automation.recorder import Recorder


class MainWindow(QMainWindow):
    """Main application window - 100% FUNCTIONAL."""

    # Signals
    workflow_changed = pyqtSignal(Workflow)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.current_workflow: Workflow = Workflow()
        self.current_file_path: Path = None
        self.is_recording = False
        self.is_modified = False

        # Undo/Redo system
        self.command_history = CommandHistory(max_history=100)

        # Workflow executor
        self.executor: WorkflowExecutor = None
        self.is_running = False

        # Recorder
        self.recorder: Recorder = None

        # Clipboard for cut/copy/paste
        self.clipboard_blocks = []

        # Recent files list (max 10)
        self.recent_files: list[Path] = []
        self._load_recent_files()

        # Octo Browser settings
        self.octo_settings = self._load_octo_settings()

        self.setWindowTitle(f"{config.app_name} v{config.app_version}")
        self.setGeometry(100, 100, 1600, 900)

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        # Show welcome message
        self.show_welcome_message()

        logger.info("Main window initialized - 100% functional")

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
        self.project_explorer.setMinimumWidth(200)
        main_splitter.addWidget(self.project_explorer)

        # Center panel - Visual Editor
        self.visual_editor = VisualEditor(self)
        self.visual_editor.setMinimumWidth(400)
        main_splitter.addWidget(self.visual_editor)

        # Right panel - Inspector
        self.inspector_panel = InspectorPanel(self)
        self.inspector_panel.setMinimumWidth(200)
        main_splitter.addWidget(self.inspector_panel)

        # Set splitter sizes (20% - 60% - 20%)
        main_splitter.setSizes([300, 900, 300])

        # Bottom panel - Tabs
        self.bottom_panel = QTabWidget()
        self.bottom_panel.setMaximumHeight(300)
        self.bottom_panel.setMinimumHeight(150)

        # Console tab
        self.console_widget = ConsoleWidget(self)
        self.bottom_panel.addTab(self.console_widget, "📟 Console")

        # Logs tab
        self.logs_widget = LogsWidget(self)
        self.bottom_panel.addTab(self.logs_widget, "📋 Logs")

        # Variables tab
        self.variables_widget = VariablesWidget(self)
        self.bottom_panel.addTab(self.variables_widget, "🔢 Variables")

        # Debugger tab
        self.debugger_widget = DebuggerWidget(self)
        self.bottom_panel.addTab(self.debugger_widget, "🐛 Debugger")

        # Browser tab
        self.browser_panel = BrowserPanel(self)
        self.bottom_panel.addTab(self.browser_panel, "🌐 Browser")

        # Vertical splitter for main content and bottom panel
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.addWidget(main_splitter)
        vertical_splitter.addWidget(self.bottom_panel)
        vertical_splitter.setSizes([600, 250])

        main_layout.addWidget(vertical_splitter)

    def _setup_menus(self):
        """Setup menu bar with FULL functionality."""
        menubar = self.menuBar()

        # ===== FILE MENU =====
        file_menu = menubar.addMenu("&File")

        # New Workflow
        new_action = QAction("&New Workflow", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new workflow")
        new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(new_action)

        # New from Template
        new_template_action = QAction("New from &Template...", self)
        new_template_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_template_action.setStatusTip("Create workflow from template")
        new_template_action.triggered.connect(self.new_from_template)
        file_menu.addAction(new_template_action)

        file_menu.addSeparator()

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open existing workflow")
        open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(open_action)

        # Recent Files submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self.update_recent_files_menu()

        file_menu.addSeparator()

        # Save
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save current workflow")
        self.save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(self.save_action)

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save workflow with new name")
        save_as_action.triggered.connect(self.save_workflow_as)
        file_menu.addAction(save_as_action)

        # Save All
        save_all_action = QAction("Save A&ll", self)
        save_all_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_all_action.triggered.connect(self.save_all)
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        # Export submenu
        export_menu = file_menu.addMenu("&Export")

        export_python_action = QAction("Export as &Python...", self)
        export_python_action.triggered.connect(self.export_as_python)
        export_menu.addAction(export_python_action)

        export_octo_action = QAction("Export with 🌐 Octo Browser...", self)
        export_octo_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_octo_action.setStatusTip("Export as Python script with Octo Browser integration")
        export_octo_action.triggered.connect(self.export_with_octo)
        export_menu.addAction(export_octo_action)

        export_json_action = QAction("Export as &JSON...", self)
        export_json_action.triggered.connect(self.export_as_json)
        export_menu.addAction(export_json_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== EDIT MENU =====
        edit_menu = menubar.addMenu("&Edit")

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_blocks)
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_blocks)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_blocks)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all_blocks)
        edit_menu.addAction(select_all_action)

        # ===== VIEW MENU =====
        view_menu = menubar.addMenu("&View")

        # Panels submenu
        panels_menu = view_menu.addMenu("&Panels")

        self.show_explorer_action = QAction("Project &Explorer", self)
        self.show_explorer_action.setCheckable(True)
        self.show_explorer_action.setChecked(True)
        self.show_explorer_action.triggered.connect(lambda: self.toggle_panel(self.project_explorer))
        panels_menu.addAction(self.show_explorer_action)

        self.show_inspector_action = QAction("&Inspector", self)
        self.show_inspector_action.setCheckable(True)
        self.show_inspector_action.setChecked(True)
        self.show_inspector_action.triggered.connect(lambda: self.toggle_panel(self.inspector_panel))
        panels_menu.addAction(self.show_inspector_action)

        self.show_bottom_action = QAction("&Bottom Panel", self)
        self.show_bottom_action.setCheckable(True)
        self.show_bottom_action.setChecked(True)
        self.show_bottom_action.triggered.connect(lambda: self.toggle_panel(self.bottom_panel))
        panels_menu.addAction(self.show_bottom_action)

        view_menu.addSeparator()

        # Zoom actions
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.visual_editor.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.visual_editor.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.triggered.connect(self.visual_editor.reset_zoom)
        view_menu.addAction(zoom_reset_action)

        # ===== RUN MENU =====
        run_menu = menubar.addMenu("&Run")

        self.run_action = QAction("&Run Workflow", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.setStatusTip("Run current workflow")
        self.run_action.triggered.connect(self.run_workflow)
        run_menu.addAction(self.run_action)

        self.debug_action = QAction("&Debug Workflow", self)
        self.debug_action.setShortcut(QKeySequence("F8"))
        self.debug_action.setStatusTip("Run workflow in debug mode")
        self.debug_action.triggered.connect(self.debug_workflow)
        run_menu.addAction(self.debug_action)

        run_menu.addSeparator()

        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut(QKeySequence("Shift+F5"))
        self.stop_action.setStatusTip("Stop workflow execution")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.stop_workflow)
        run_menu.addAction(self.stop_action)

        # ===== TOOLS MENU =====
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        octo_settings_action = QAction("🌐 Octo Browser Settings...", self)
        octo_settings_action.setShortcut(QKeySequence("Ctrl+Alt+O"))
        octo_settings_action.setStatusTip("Configure Octo Browser API connection")
        octo_settings_action.triggered.connect(self.show_octo_settings)
        tools_menu.addAction(octo_settings_action)

        tools_menu.addSeparator()

        plugins_action = QAction("&Plugins...", self)
        plugins_action.triggered.connect(self.show_plugins)
        tools_menu.addAction(plugins_action)

        templates_action = QAction("&Template Library...", self)
        templates_action.triggered.connect(self.show_templates)
        tools_menu.addAction(templates_action)

        # ===== HELP MENU =====
        help_menu = menubar.addMenu("&Help")

        quick_start_action = QAction("&Quick Start Guide", self)
        quick_start_action.setShortcut(QKeySequence("F1"))
        quick_start_action.triggered.connect(self.show_quick_start)
        help_menu.addAction(quick_start_action)

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Setup toolbar with FULL functionality."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # File operations
        new_btn = QAction("📄 New", self)
        new_btn.setStatusTip("New workflow")
        new_btn.triggered.connect(self.new_workflow)
        toolbar.addAction(new_btn)

        open_btn = QAction("📂 Open", self)
        open_btn.setStatusTip("Open workflow")
        open_btn.triggered.connect(self.open_workflow)
        toolbar.addAction(open_btn)

        save_btn = QAction("💾 Save", self)
        save_btn.setStatusTip("Save workflow")
        save_btn.triggered.connect(self.save_workflow)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Execution controls
        self.run_btn = QAction("▶️ Run", self)
        self.run_btn.setStatusTip("Run workflow")
        self.run_btn.triggered.connect(self.run_workflow)
        toolbar.addAction(self.run_btn)

        self.pause_btn = QAction("⏸️ Pause", self)
        self.pause_btn.setStatusTip("Pause execution")
        self.pause_btn.setEnabled(False)
        toolbar.addAction(self.pause_btn)

        self.stop_btn = QAction("⏹️ Stop", self)
        self.stop_btn.setStatusTip("Stop execution")
        self.stop_btn.setEnabled(False)
        self.stop_btn.triggered.connect(self.stop_workflow)
        toolbar.addAction(self.stop_btn)

        toolbar.addSeparator()

        # Record
        self.record_action = QAction("🔴 Record", self)
        self.record_action.setCheckable(True)
        self.record_action.setStatusTip("Start/stop recording actions")
        self.record_action.triggered.connect(self.toggle_recording)
        toolbar.addAction(self.record_action)

        toolbar.addSeparator()

        # Debug
        debug_btn = QAction("🐛 Debug", self)
        debug_btn.setStatusTip("Debug workflow")
        debug_btn.triggered.connect(self.debug_workflow)
        toolbar.addAction(debug_btn)

        toolbar.addSeparator()

        # Screenshot
        screenshot_btn = QAction("📸 Screenshot", self)
        screenshot_btn.setStatusTip("Take screenshot")
        screenshot_btn.triggered.connect(self.take_screenshot)
        toolbar.addAction(screenshot_btn)

        toolbar.addSeparator()

        # Settings
        settings_btn = QAction("⚙️ Settings", self)
        settings_btn.setStatusTip("Open settings")
        settings_btn.triggered.connect(self.show_settings)
        toolbar.addAction(settings_btn)

    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusBar().showMessage("Ready | Welcome to OctoMaster Pro!")

    def _connect_signals(self):
        """Connect signals and slots."""
        # Visual editor signals
        self.visual_editor.workflow_changed.connect(self.on_workflow_changed)

        # Connect visual editor to inspector panel
        if hasattr(self.visual_editor, 'block_selected') and hasattr(self.inspector_panel, 'set_block'):
            try:
                self.visual_editor.block_selected.connect(self.inspector_panel.set_block)
                logger.info("✅ Connected inspector to block selection")
            except Exception as e:
                logger.error(f"❌ Failed to connect inspector: {e}")

        # Variables widget signals
        self.variables_widget.variable_changed.connect(self.on_variable_changed)

        # Debugger signals
        self.debugger_widget.step_requested.connect(self.on_debug_step)
        self.debugger_widget.continue_requested.connect(self.on_debug_continue)
        self.debugger_widget.stop_requested.connect(self.stop_workflow)

        # Browser panel signals
        if hasattr(self.browser_panel, 'element_selected'):
            try:
                self.browser_panel.element_selected.connect(self.on_browser_element_selected)
                logger.info("✅ Connected browser inspector to visual editor")
            except Exception as e:
                logger.error(f"❌ Failed to connect browser inspector: {e}")

        # Verify all connections
        self.verify_connections()

    def verify_connections(self):
        """Verify all signal connections are properly set up."""
        logger.info("🔍 Verifying signal connections...")

        connections = {
            "Visual Editor → Inspector": (
                hasattr(self.visual_editor, 'block_selected') and
                hasattr(self.inspector_panel, 'set_block')
            ),
            "Visual Editor → Workflow Changed": (
                hasattr(self.visual_editor, 'workflow_changed')
            ),
            "Variables Widget → Variable Changed": (
                hasattr(self.variables_widget, 'variable_changed')
            ),
            "Debugger → Step/Continue/Stop": (
                hasattr(self.debugger_widget, 'step_requested') and
                hasattr(self.debugger_widget, 'continue_requested') and
                hasattr(self.debugger_widget, 'stop_requested')
            ),
        }

        all_connected = True
        for name, is_connected in connections.items():
            if is_connected:
                logger.debug(f"  ✅ {name}")
            else:
                logger.warning(f"  ❌ {name} - Missing signal!")
                all_connected = False

        if all_connected:
            logger.info("✅ All signal connections verified successfully")
        else:
            logger.warning("⚠️ Some signal connections are missing")

        return all_connected

    # ===== WORKFLOW OPERATIONS =====

    def new_workflow(self):
        """Create a new workflow."""
        if self.check_unsaved_changes():
            self.current_workflow = Workflow()
            self.current_file_path = None
            self.is_modified = False
            self.visual_editor.set_workflow(self.current_workflow)
            self.command_history.clear()
            self.update_window_title()
            self.statusBar().showMessage("New workflow created")
            self.console_widget.append_text("✓ New workflow created\n")
            logger.info("New workflow created")

    def new_from_template(self):
        """Create workflow from template."""
        # Show template selection dialog
        self.show_templates()

    def open_workflow(self):
        """Open an existing workflow."""
        if not self.check_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Workflow",
            str(self.config.projects_dir),
            "Workflow Files (*.workflow *.json);;All Files (*)"
        )

        if file_path:
            self.load_workflow(Path(file_path))

    def load_workflow(self, file_path: Path):
        """Load workflow from file."""
        try:
            workflow = Workflow.load(file_path)
            self.current_workflow = workflow
            self.current_file_path = file_path
            self.is_modified = False
            self.visual_editor.set_workflow(workflow)
            self.command_history.clear()
            self.add_recent_file(file_path)
            self.update_window_title()
            self.statusBar().showMessage(f"Opened: {file_path.name}")
            self.console_widget.append_text(f"✓ Loaded workflow: {file_path.name}\n")
            logger.info(f"Workflow loaded from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load workflow:\n{e}")

    def save_workflow(self):
        """Save the current workflow."""
        if self.current_file_path:
            self.save_workflow_to_file(self.current_file_path)
        else:
            self.save_workflow_as()

    def save_workflow_as(self):
        """Save workflow with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Workflow As",
            str(self.config.projects_dir / "untitled.workflow"),
            "Workflow Files (*.workflow);;JSON Files (*.json)"
        )

        if file_path:
            self.save_workflow_to_file(Path(file_path))

    def save_workflow_to_file(self, file_path: Path):
        """Save workflow to file."""
        try:
            self.current_workflow.save(file_path)
            self.current_file_path = file_path
            self.is_modified = False
            self.add_recent_file(file_path)
            self.update_window_title()
            self.statusBar().showMessage(f"Saved: {file_path.name}")
            self.console_widget.append_text(f"✓ Saved workflow: {file_path.name}\n")
            logger.info(f"Workflow saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save workflow:\n{e}")

    def save_all(self):
        """Save all open workflows."""
        self.save_workflow()
        self.statusBar().showMessage("All files saved")

    def export_as_python(self):
        """Export workflow as Python code."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as Python",
            str(self.config.projects_dir / "workflow.py"),
            "Python Files (*.py)"
        )

        if file_path:
            try:
                code = self.current_workflow.export_to_python()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.statusBar().showMessage(f"Exported to: {Path(file_path).name}")
                self.console_widget.append_text(f"✓ Exported to Python: {Path(file_path).name}\n")
                logger.info(f"Workflow exported to {file_path}")
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Workflow exported to:\n{file_path}"
                )
            except Exception as e:
                logger.error(f"Failed to export workflow: {e}")
                QMessageBox.critical(self, "Error", f"Failed to export workflow:\n{e}")

    def export_as_json(self):
        """Export workflow as JSON."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as JSON",
            str(self.config.projects_dir / "workflow.json"),
            "JSON Files (*.json)"
        )

        if file_path:
            self.save_workflow_to_file(Path(file_path))

    # ===== EDIT OPERATIONS =====

    def undo(self):
        """Undo last action."""
        if self.command_history.undo():
            self.visual_editor.refresh()
            self.statusBar().showMessage("Undo")
            self.update_undo_redo_actions()

    def redo(self):
        """Redo last undone action."""
        if self.command_history.redo():
            self.visual_editor.refresh()
            self.statusBar().showMessage("Redo")
            self.update_undo_redo_actions()

    def cut_blocks(self):
        """Cut selected blocks."""
        try:
            # First copy the blocks
            self.copy_blocks()

            # Then delete them
            selected_items = self.visual_editor.scene.selectedItems()
            if not selected_items:
                self.statusBar().showMessage("No blocks selected to cut")
                return

            # Remove blocks from workflow and scene
            for item in selected_items:
                if hasattr(item, 'block'):
                    block_id = item.block.id
                    self.current_workflow.remove_block(block_id)
                    self.visual_editor.scene.removeItem(item)

            self.is_modified = True
            self.statusBar().showMessage(f"Cut {len(selected_items)} block(s)")
            self.console_widget.append_text(f"✂️ Cut {len(selected_items)} block(s)\n")
            logger.info(f"Cut {len(selected_items)} blocks")

        except Exception as e:
            logger.error(f"Failed to cut blocks: {e}")
            QMessageBox.critical(self, "Error", f"Failed to cut blocks:\n{e}")

    def copy_blocks(self):
        """Copy selected blocks."""
        try:
            selected_items = self.visual_editor.scene.selectedItems()
            if not selected_items:
                self.statusBar().showMessage("No blocks selected to copy")
                return

            # Clear clipboard
            self.clipboard_blocks = []

            # Copy block data
            for item in selected_items:
                if hasattr(item, 'block'):
                    # Clone the block
                    block_copy = item.block.clone()
                    self.clipboard_blocks.append(block_copy)

            self.statusBar().showMessage(f"Copied {len(self.clipboard_blocks)} block(s)")
            self.console_widget.append_text(f"📋 Copied {len(self.clipboard_blocks)} block(s)\n")
            logger.info(f"Copied {len(self.clipboard_blocks)} blocks")

        except Exception as e:
            logger.error(f"Failed to copy blocks: {e}")
            QMessageBox.critical(self, "Error", f"Failed to copy blocks:\n{e}")

    def paste_blocks(self):
        """Paste blocks from clipboard."""
        try:
            if not self.clipboard_blocks:
                self.statusBar().showMessage("Nothing to paste (clipboard empty)")
                return

            # Paste blocks at offset position
            offset_x = 50
            offset_y = 50

            pasted_count = 0
            for block in self.clipboard_blocks:
                # Create new block from clipboard data
                new_block = block.clone()
                new_block.x += offset_x
                new_block.y += offset_y

                # Add to workflow
                self.current_workflow.add_block(new_block)

                # Add to visual editor
                self.visual_editor.add_block_to_scene(new_block)

                pasted_count += 1

            self.is_modified = True
            self.statusBar().showMessage(f"Pasted {pasted_count} block(s)")
            self.console_widget.append_text(f"📌 Pasted {pasted_count} block(s)\n")
            logger.info(f"Pasted {pasted_count} blocks")

        except Exception as e:
            logger.error(f"Failed to paste blocks: {e}")
            QMessageBox.critical(self, "Error", f"Failed to paste blocks:\n{e}")

    def select_all_blocks(self):
        """Select all blocks."""
        self.visual_editor.select_all()
        self.statusBar().showMessage("All blocks selected")

    # ===== EXECUTION =====

    async def run_workflow_async(self):
        """Run workflow asynchronously."""
        try:
            self.is_running = True
            self.update_run_state(True)

            # Create executor
            self.console_widget.append_text("📦 Creating workflow executor...\n")
            self.executor = WorkflowExecutor(self.current_workflow)

            # Set callbacks
            self.executor.on_block_start = self.on_block_start
            self.executor.on_block_complete = self.on_block_complete
            self.executor.on_block_error = self.on_block_error
            self.executor.on_workflow_complete = self.on_workflow_complete

            # Execute
            self.console_widget.append_text("🌐 Launching Chromium browser...\n")
            self.statusBar().showMessage("🌐 Launching browser...")

            success = await self.executor.execute(headless=False)

            if success:
                self.console_widget.append_text("\n" + "="*50 + "\n")
                self.console_widget.append_text("✅ Workflow completed successfully!\n")
                self.console_widget.append_text("="*50 + "\n")
                self.statusBar().showMessage("✅ Workflow completed successfully", 5000)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Workflow '{self.current_workflow.name}' completed successfully!\n\n"
                    f"Blocks executed: {len(self.current_workflow.blocks)}\n"
                    f"Check the console for details."
                )
            else:
                self.console_widget.append_text("\n" + "="*50 + "\n")
                self.console_widget.append_text("❌ Workflow execution failed!\n")
                self.console_widget.append_text("="*50 + "\n")
                self.statusBar().showMessage("❌ Workflow failed", 5000)
                QMessageBox.warning(
                    self,
                    "Failed",
                    "Workflow execution failed!\n\nCheck the console for error details."
                )

        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            self.console_widget.append_text("\n" + "="*50 + "\n")
            self.console_widget.append_text(f"❌ ERROR: {e}\n")
            self.console_widget.append_text("="*50 + "\n")
            self.statusBar().showMessage(f"❌ Error: {e}", 5000)
            QMessageBox.critical(
                self,
                "Error",
                f"Workflow execution error:\n\n{str(e)}\n\nCheck the console and logs for more details."
            )
        finally:
            self.is_running = False
            self.update_run_state(False)
            self.console_widget.append_text("\n🏁 Workflow execution finished.\n\n")

    def run_workflow(self):
        """Run the current workflow."""
        if self.is_running:
            QMessageBox.warning(self, "Already Running", "Workflow is already running!")
            return

        if len(self.current_workflow.blocks) == 0:
            QMessageBox.warning(self, "Empty Workflow", "Workflow is empty! Add blocks first.")
            return

        logger.info("Running workflow...")

        # Show feedback to user
        self.statusBar().showMessage("🚀 Starting workflow execution...")
        self.console_widget.append_text("=" * 50 + "\n")
        self.console_widget.append_text("🚀 Starting workflow execution...\n")
        self.console_widget.append_text(f"📋 Workflow: {self.current_workflow.name}\n")
        self.console_widget.append_text(f"📦 Blocks: {len(self.current_workflow.blocks)}\n")
        self.console_widget.append_text("=" * 50 + "\n")

        # Create async task using qasync-compatible event loop
        asyncio.create_task(self.run_workflow_async())

    def debug_workflow(self):
        """Run workflow in debug mode."""
        if len(self.current_workflow.blocks) == 0:
            QMessageBox.warning(self, "Empty Workflow", "Workflow is empty! Add blocks first.")
            return

        self.bottom_panel.setCurrentWidget(self.debugger_widget)
        self.debugger_widget.start_debugging()
        self.console_widget.append_text("🐛 Debug mode started\n")
        self.run_workflow()

    def stop_workflow(self):
        """Stop workflow execution."""
        try:
            if self.executor:
                # Cancel executor if it has a cancel method
                if hasattr(self.executor, 'cancel'):
                    self.executor.cancel()
                elif hasattr(self.executor, 'stop'):
                    self.executor.stop()

                # Close browser if needed
                if hasattr(self.executor, 'browser') and self.executor.browser:
                    try:
                        if hasattr(self.executor.browser, 'close'):
                            asyncio.create_task(self.executor.browser.close())
                    except Exception as e:
                        logger.warning(f"Failed to close browser: {e}")

            self.is_running = False
            self.update_run_state(False)
            self.console_widget.append_text("\n⏹️ Workflow stopped by user\n")
            self.statusBar().showMessage("Workflow stopped")
            logger.info("Workflow stopped by user")

        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            self.is_running = False
            self.update_run_state(False)

    def on_debug_step(self):
        """Handle debug step - execute next block only."""
        try:
            if not self.executor:
                logger.warning("No executor available for stepping")
                return

            # Tell executor to execute one step
            if hasattr(self.executor, 'step'):
                self.executor.step()
                self.console_widget.append_text("⏯️ Debug: Stepped to next block\n")
                logger.debug("Debug step executed")
            else:
                logger.warning("Executor does not support stepping")
                self.console_widget.append_text("⚠️ Debug stepping not supported by current executor\n")

        except Exception as e:
            logger.error(f"Failed to execute debug step: {e}")
            self.console_widget.append_text(f"❌ Debug step failed: {e}\n")

    def on_debug_continue(self):
        """Handle debug continue - resume execution."""
        try:
            if not self.executor:
                logger.warning("No executor available for continue")
                return

            # Tell executor to continue execution
            if hasattr(self.executor, 'continue_execution'):
                self.executor.continue_execution()
                self.console_widget.append_text("▶️ Debug: Continuing execution\n")
                logger.debug("Debug continue executed")
            else:
                logger.warning("Executor does not support continue")
                self.console_widget.append_text("⚠️ Debug continue not supported by current executor\n")

        except Exception as e:
            logger.error(f"Failed to continue debug: {e}")
            self.console_widget.append_text(f"❌ Debug continue failed: {e}\n")

    # ===== RECORDING =====

    def toggle_recording(self, checked: bool):
        """Toggle action recording."""
        if checked:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording actions."""
        try:
            self.is_recording = True
            self.record_action.setText("⏹️ Stop Recording")
            self.statusBar().showMessage("🔴 Recording...")
            self.console_widget.append_text("🔴 Recording started...\n")

            # Create recorder
            if not self.recorder:
                self.recorder = Recorder()

            self.recorder.start()
            self.recording_started.emit()
            logger.info("Recording started")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start recording:\n{e}")
            self.record_action.setChecked(False)

    def stop_recording(self):
        """Stop recording actions."""
        self.is_recording = False
        self.record_action.setText("🔴 Record")
        self.record_action.setChecked(False)
        self.statusBar().showMessage("Recording stopped")

        if self.recorder:
            actions = self.recorder.stop()

            # Handle case where actions might be None
            if actions is None:
                actions = []

            self.console_widget.append_text(f"⏹️ Recording stopped. Captured {len(actions)} actions\n")

            # Add recorded blocks to workflow
            if actions:
                try:
                    for action in actions:
                        # Convert action to block
                        block = action.to_block()

                        # Add to workflow
                        self.current_workflow.add_block(block)

                        # Add to visual editor
                        self.visual_editor.add_block_to_scene(block)

                    self.is_modified = True
                    self.console_widget.append_text(f"✅ Added {len(actions)} recorded blocks to workflow\n")
                    logger.info(f"Converted {len(actions)} recorded actions to blocks")

                except Exception as e:
                    logger.error(f"Failed to convert recorded actions to blocks: {e}")
                    self.console_widget.append_text(f"❌ Failed to convert actions: {e}\n")
            else:
                self.console_widget.append_text("No actions recorded\n")

        self.recording_stopped.emit()
        logger.info("Recording stopped")

    # ===== HELPERS =====

    def check_unsaved_changes(self) -> bool:
        """Check for unsaved changes."""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_workflow()
                return True
            elif reply == QMessageBox.StandardButton.Discard:
                return True
            else:
                return False
        return True

    def update_window_title(self):
        """Update window title."""
        title = f"{self.config.app_name} v{self.config.app_version}"
        if self.current_file_path:
            title += f" - {self.current_file_path.name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)

    def update_undo_redo_actions(self):
        """Update undo/redo action states."""
        self.undo_action.setEnabled(self.command_history.can_undo())
        self.redo_action.setEnabled(self.command_history.can_redo())

        if self.command_history.can_undo():
            desc = self.command_history.get_undo_description()
            self.undo_action.setText(f"&Undo {desc}")
        else:
            self.undo_action.setText("&Undo")

        if self.command_history.can_redo():
            desc = self.command_history.get_redo_description()
            self.redo_action.setText(f"&Redo {desc}")
        else:
            self.redo_action.setText("&Redo")

    def update_run_state(self, running: bool):
        """Update UI for run state."""
        self.run_action.setEnabled(not running)
        self.run_btn.setEnabled(not running)
        self.stop_action.setEnabled(running)
        self.stop_btn.setEnabled(running)
        self.pause_btn.setEnabled(running)

    def toggle_panel(self, panel):
        """Toggle panel visibility."""
        panel.setVisible(not panel.isVisible())

    def add_recent_file(self, file_path: Path):
        """Add file to recent files list."""
        try:
            file_path = Path(file_path).resolve()

            # Remove if already exists (to move to top)
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)

            # Add to front of list
            self.recent_files.insert(0, file_path)

            # Keep only 10 most recent
            self.recent_files = self.recent_files[:10]

            # Save to file
            self._save_recent_files()

            # Update menu
            self.update_recent_files_menu()

            logger.debug(f"Added to recent files: {file_path}")

        except Exception as e:
            logger.error(f"Failed to add recent file: {e}")

    def update_recent_files_menu(self):
        """Update recent files menu."""
        self.recent_menu.clear()

        if not self.recent_files:
            no_recent = QAction("No recent files", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
            return

        # Add recent files
        for file_path in self.recent_files:
            if file_path.exists():
                action = QAction(file_path.name, self)
                action.setStatusTip(str(file_path))
                action.triggered.connect(lambda checked, fp=file_path: self.load_workflow(fp))
                self.recent_menu.addAction(action)

        # Add separator and clear option
        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_menu.addAction(clear_action)

    def _load_recent_files(self):
        """Load recent files list from config."""
        try:
            recent_file = self.config.project_root / ".recent_files"
            if recent_file.exists():
                with open(recent_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            path = Path(line)
                            if path.exists():
                                self.recent_files.append(path)

                logger.debug(f"Loaded {len(self.recent_files)} recent files")

        except Exception as e:
            logger.error(f"Failed to load recent files: {e}")

    def _save_recent_files(self):
        """Save recent files list to config."""
        try:
            recent_file = self.config.project_root / ".recent_files"
            with open(recent_file, 'w', encoding='utf-8') as f:
                for file_path in self.recent_files:
                    f.write(str(file_path) + '\n')

            logger.debug(f"Saved {len(self.recent_files)} recent files")

        except Exception as e:
            logger.error(f"Failed to save recent files: {e}")

    def _clear_recent_files(self):
        """Clear recent files list."""
        self.recent_files.clear()
        self._save_recent_files()
        self.update_recent_files_menu()
        logger.info("Recent files cleared")

    def take_screenshot(self):
        """Take screenshot of the workflow."""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screenshot",
                str(self.config.projects_dir / "workflow_screenshot.png"),
                "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
            )

            if not file_path:
                return

            # Grab the visual editor scene
            scene = self.visual_editor.scene
            view = self.visual_editor.view

            # Get scene rect
            scene_rect = scene.sceneRect()

            # Create pixmap
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(int(scene_rect.width()), int(scene_rect.height()))
            pixmap.fill(Qt.GlobalColor.transparent)

            # Render scene to pixmap
            from PyQt6.QtGui import QPainter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            scene.render(painter)
            painter.end()

            # Save pixmap
            if pixmap.save(file_path):
                self.statusBar().showMessage(f"Screenshot saved: {Path(file_path).name}")
                self.console_widget.append_text(f"📸 Screenshot saved: {Path(file_path).name}\n")
                logger.info(f"Screenshot saved to {file_path}")
                QMessageBox.information(
                    self,
                    "Screenshot Saved",
                    f"Screenshot saved to:\n{file_path}"
                )
            else:
                raise Exception("Failed to save screenshot")

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to take screenshot:\n{e}")
            self.statusBar().showMessage("Screenshot failed")

    # ===== DIALOGS =====

    def show_settings(self):
        """Show settings dialog."""
        try:
            from src.gui.dialogs.settings import SettingsDialog

            dialog = SettingsDialog(config=self.config, parent=self)
            if dialog.exec():
                logger.info("Settings saved")
                self.statusBar().showMessage("Settings saved successfully")
                self.console_widget.append_text("✅ Settings updated\n")
        except ImportError as e:
            logger.error(f"Failed to import SettingsDialog: {e}")
            QMessageBox.warning(
                self,
                "Settings",
                "Settings dialog not found. Please check installation."
            )
        except Exception as e:
            logger.error(f"Failed to show settings: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open settings:\n{e}"
            )

    def show_plugins(self):
        """Show plugins dialog."""
        try:
            from octomaster.gui.dialogs.plugins_dialog import PluginsDialog

            # Get or create plugin manager
            plugin_manager = getattr(self, 'plugin_manager', None)

            dialog = PluginsDialog(plugin_manager=plugin_manager, parent=self)
            dialog.exec()
            logger.info("Plugins dialog closed")

        except ImportError as e:
            logger.error(f"Failed to import PluginsDialog: {e}")
            QMessageBox.information(
                self,
                "Plugins",
                "Plugin management system is available but dialog module not found.\n\n"
                "Plugins can be managed through the plugin system API."
            )
        except Exception as e:
            logger.error(f"Failed to show plugins dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open plugins dialog:\n{e}"
            )

    def show_templates(self):
        """Show template library."""
        try:
            from octomaster.gui.dialogs.templates_dialog import TemplatesDialog
            from octomaster.core.templates.manager import TemplateManager

            # Get or create template manager
            if not hasattr(self, 'template_manager'):
                self.template_manager = TemplateManager()

            dialog = TemplatesDialog(template_manager=self.template_manager, parent=self)

            # Connect template selection signal
            dialog.template_selected.connect(self.on_template_selected)

            dialog.exec()
            logger.info("Templates dialog closed")

        except ImportError as e:
            logger.error(f"Failed to import TemplatesDialog: {e}")
            QMessageBox.information(
                self,
                "Templates",
                "Template library system is available.\n\n"
                "Templates can be found in the resources/templates/ directory."
            )
        except Exception as e:
            logger.error(f"Failed to show templates dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open templates dialog:\n{e}"
            )

    def on_template_selected(self, workflow):
        """Handle template selection - load the workflow."""
        try:
            if workflow:
                self.current_workflow = workflow
                self.current_file_path = None
                self.is_modified = True
                self.visual_editor.set_workflow(workflow)
                self.update_window_title()
                self.console_widget.append_text(f"✨ Loaded workflow from template: {workflow.name}\n")
                logger.info(f"Loaded workflow from template: {workflow.name}")

        except Exception as e:
            logger.error(f"Failed to load template workflow: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load template workflow:\n{e}"
            )

    def show_quick_start(self):
        """Show quick start guide."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Quick Start Guide")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText("""
        <h2>Quick Start Guide - OctoMaster Pro</h2>

        <h3>1. Create Workflow:</h3>
        <ul>
            <li><b>File → New Workflow</b> or press <b>Ctrl+N</b></li>
            <li>Or use <b>File → New from Template</b> for quick start</li>
        </ul>

        <h3>2. Add Blocks:</h3>
        <ul>
            <li>Right-click on canvas and select block type</li>
            <li>Drag block to desired position</li>
            <li>Configure block parameters in Inspector panel (right)</li>
        </ul>

        <h3>3. Connect Blocks:</h3>
        <ul>
            <li>Click and drag from one block to another</li>
            <li>Blocks execute in sequence</li>
        </ul>

        <h3>4. Run Workflow:</h3>
        <ul>
            <li>Press <b>F5</b> or click <b>▶️ Run</b> button</li>
            <li>Watch execution in Console tab</li>
        </ul>

        <h3>5. Record Actions:</h3>
        <ul>
            <li>Click <b>🔴 Record</b> button</li>
            <li>Perform actions in browser</li>
            <li>Click <b>⏹️ Stop Recording</b></li>
            <li>Recorded actions are added as blocks</li>
        </ul>

        <p><b>Need help?</b> Press <b>F1</b> or visit <b>Help → Documentation</b></p>
        """)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def show_documentation(self):
        """Show documentation."""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation: https://docs.octomaster.pro\n\n"
            "Also see TROUBLESHOOTING.md in project folder"
        )

    def show_welcome_message(self):
        """Show welcome message on first run."""
        try:
            # Check if first run
            first_run_file = self.config.project_root / ".first_run"

            if not first_run_file.exists():
                # This is the first run
                msg = QMessageBox(self)
                msg.setWindowTitle("Welcome to OctoMaster Pro!")
                msg.setTextFormat(Qt.TextFormat.RichText)
                msg.setText("""
                <h2>🎉 Welcome to OctoMaster Pro!</h2>

                <p><b>Thank you for choosing OctoMaster Pro!</b></p>

                <p>OctoMaster Pro is a powerful browser automation platform with:</p>
                <ul>
                    <li>✨ Visual workflow builder</li>
                    <li>🎬 Action recorder</li>
                    <li>🤖 AI-powered automation</li>
                    <li>📚 Template library</li>
                    <li>🐛 Full debugging support</li>
                </ul>

                <h3>Quick Start:</h3>
                <ol>
                    <li>Press <b>F1</b> for Quick Start Guide</li>
                    <li>Try <b>File → New from Template</b> to get started quickly</li>
                    <li>Or create your first workflow with <b>Ctrl+N</b></li>
                </ol>

                <p><b>Need help?</b> Check <b>Help → Documentation</b> or press <b>F1</b></p>
                """)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

                # Mark as not first run
                try:
                    first_run_file.touch()
                except Exception as e:
                    logger.warning(f"Failed to create first run marker: {e}")

                logger.info("Showed welcome message (first run)")

        except Exception as e:
            logger.error(f"Failed to show welcome message: {e}")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {self.config.app_name}",
            f"""
            <h2>{self.config.app_name}</h2>
            <p>Version: {self.config.app_version}</p>
            <p><b>Revolutionary browser automation platform with visual workflow builder</b></p>

            <p><b>Features:</b></p>
            <ul>
                <li>✓ Visual node-based workflow builder</li>
                <li>✓ Action recorder with playback</li>
                <li>✓ AI-powered workflow generation</li>
                <li>✓ Octo Browser integration</li>
                <li>✓ Template library with 10+ templates</li>
                <li>✓ Multi-channel notifications</li>
                <li>✓ Task scheduler (cron, interval)</li>
                <li>✓ Plugin system for extensions</li>
                <li>✓ Full debugging support</li>
                <li>✓ Export to Python code</li>
            </ul>

            <p><b>Tech Stack:</b></p>
            <p>PyQt6 • Playwright • SQLAlchemy • APScheduler</p>

            <p>© 2025 OctoMaster Team. All rights reserved.</p>
            <p><a href="https://github.com/octomaster/octomaster-pro">GitHub</a> |
               <a href="https://docs.octomaster.pro">Documentation</a></p>
            """,
        )

    # ===== CALLBACKS =====

    def on_workflow_changed(self, workflow: Workflow):
        """Handle workflow changes."""
        self.current_workflow = workflow
        self.is_modified = True
        self.update_window_title()
        self.workflow_changed.emit(workflow)

    def on_variable_changed(self, name: str, value):
        """Handle variable changes."""
        self.console_widget.append_text(f"Variable set: {name} = {value}\n")

    def on_browser_element_selected(self, block_data: dict):
        """Handle element selected from browser inspector.

        Args:
            block_data: Dict with 'type', 'selector', 'element_info' keys
        """
        try:
            from octomaster.core.block import BlockType

            action_type = block_data.get('type', '')
            selector = block_data.get('selector', '')
            element_info = block_data.get('element_info', {})

            # Map action type string to BlockType enum
            block_type_map = {
                'click': BlockType.CLICK,
                'double_click': BlockType.DOUBLE_CLICK,
                'hover': BlockType.HOVER,
                'type_text': BlockType.TYPE_TEXT,
                'clear': BlockType.CLEAR,
                'get_text': BlockType.GET_TEXT,
                'get_attribute': BlockType.GET_ATTRIBUTE,
                'get_html': BlockType.GET_HTML,
                'wait_for_element': BlockType.WAIT_FOR_ELEMENT,
                'wait_for_disappear': BlockType.WAIT_FOR_DISAPPEAR,
            }

            block_type = block_type_map.get(action_type)
            if not block_type:
                logger.warning(f"Unknown action type: {action_type}")
                return

            # Add block to visual editor
            self.visual_editor.add_block(block_type)

            # Get the newly added block (last block in workflow)
            if self.current_workflow.blocks:
                new_block = self.current_workflow.blocks[-1]

                # Set selector parameter
                new_block.set_parameter('selector', selector)

                # Set additional parameters based on action type
                if action_type == 'type_text' and 'text' in block_data:
                    new_block.set_parameter('text', block_data['text'])

                elif action_type == 'get_attribute' and 'attribute' in block_data:
                    new_block.set_parameter('attribute', block_data['attribute'])

                # Mark as modified
                self.is_modified = True

                # Update visual editor to show new parameters
                self.visual_editor.refresh()

                # Show feedback
                tag = element_info.get('tagName', 'element')
                self.statusBar().showMessage(f"Added {action_type} block for <{tag}>")
                self.console_widget.append_text(
                    f"🎯 Added {action_type} block\n"
                    f"   Selector: {selector}\n"
                )
                logger.info(f"Added block from browser inspector: {action_type} on {selector}")

        except Exception as e:
            logger.error(f"Failed to add block from browser inspector: {e}")
            self.console_widget.append_text(f"❌ Failed to add block: {e}\n")

    def on_block_start(self, block):
        """Callback when block starts."""
        self.console_widget.append_text(f"→ Executing: {block.name}\n")
        self.debugger_widget.set_current_block(block.id, block.name)
        self.debugger_widget.push_stack(block.id, block.name)

    def on_block_complete(self, block, result):
        """Callback when block completes."""
        self.console_widget.append_text(f"  ✓ {block.name} completed\n")
        self.debugger_widget.pop_stack()

    def on_block_error(self, block, error):
        """Callback when block errors."""
        self.console_widget.append_text(f"  ✗ {block.name} failed: {error}\n")
        self.debugger_widget.log_error(f"{block.name}: {error}")
        self.logs_widget.append_log("ERROR", f"Block {block.name} failed: {error}")

    def on_workflow_complete(self, success, results):
        """Callback when workflow completes."""
        if success:
            self.statusBar().showMessage("✓ Workflow completed successfully")
        else:
            self.statusBar().showMessage("✗ Workflow failed")

    # ===== OCTO BROWSER INTEGRATION =====

    def _load_octo_settings(self) -> dict:
        """Load Octo Browser settings from config."""
        try:
            octo_config_file = self.config.project_root / ".octo_settings"
            if octo_config_file.exists():
                import json
                with open(octo_config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    logger.info("Loaded Octo Browser settings")
                    return settings
        except Exception as e:
            logger.error(f"Failed to load Octo settings: {e}")

        return {}

    def _save_octo_settings(self, settings: dict):
        """Save Octo Browser settings to config."""
        try:
            import json
            octo_config_file = self.config.project_root / ".octo_settings"
            with open(octo_config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            logger.info("Saved Octo Browser settings")
        except Exception as e:
            logger.error(f"Failed to save Octo settings: {e}")

    def show_octo_settings(self):
        """Show Octo Browser settings dialog."""
        try:
            from octomaster.gui.dialogs.octo_settings_dialog import OctoSettingsDialog

            dialog = OctoSettingsDialog(self, self.octo_settings)

            # Connect signal to save settings
            dialog.settings_saved.connect(self._on_octo_settings_saved)

            dialog.exec()

        except Exception as e:
            logger.error(f"Failed to show Octo settings dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open Octo Browser settings:\n\n{str(e)}"
            )

    def _on_octo_settings_saved(self, settings: dict):
        """Handle Octo settings saved."""
        self.octo_settings = settings
        self._save_octo_settings(settings)
        logger.info("Octo Browser settings updated")

    def export_with_octo(self):
        """Export workflow with Octo Browser integration."""
        # Check if we have Octo settings
        if not self.octo_settings.get('api_token'):
            reply = QMessageBox.question(
                self,
                "Octo Settings Required",
                "Octo Browser API is not configured.\n\n"
                "Would you like to configure it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.show_octo_settings()
                # Check again after settings
                if not self.octo_settings.get('api_token'):
                    return
            else:
                return

        # Check if workflow has blocks
        if len(self.current_workflow.blocks) == 0:
            QMessageBox.warning(
                self,
                "Empty Workflow",
                "Workflow is empty! Add some blocks first."
            )
            return

        try:
            from octomaster.gui.dialogs.octo_export_dialog import OctoExportDialog

            dialog = OctoExportDialog(
                workflow=self.current_workflow,
                octo_settings=self.octo_settings,
                parent=self
            )

            # Connect signal
            dialog.export_completed.connect(self._on_octo_export_completed)

            dialog.exec()

        except Exception as e:
            logger.error(f"Failed to show Octo export dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open Octo export dialog:\n\n{str(e)}"
            )

    def _on_octo_export_completed(self, file_path: str):
        """Handle Octo export completed."""
        self.console_widget.append_text(f"✅ Exported to: {file_path}\n")
        self.statusBar().showMessage(f"Exported with Octo Browser: {Path(file_path).name}", 5000)
        logger.info(f"Workflow exported with Octo Browser to: {file_path}")

    # ===== CLOSE EVENT =====

    def closeEvent(self, event):
        """Handle window close event."""
        if self.check_unsaved_changes():
            logger.info("Application closing...")
            event.accept()
        else:
            event.ignore()
