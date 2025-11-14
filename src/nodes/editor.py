"""
Main node editor widget for visual workflow construction.

Provides complete node editor interface with block palette,
canvas, and workflow execution capabilities.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QSplitter,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from loguru import logger

from src.nodes.scene import NodeScene
from src.nodes.executor import WorkflowExecutor, ExecutionStatus
from src.nodes.serializer import WorkflowSerializer
from src.nodes.blocks import *


class BlockPalette(QListWidget):
    """Block palette for adding blocks to workflow."""

    block_requested = pyqtSignal(str)  # Block type name

    def __init__(self, parent=None) -> None:
        """Initialize block palette."""
        super().__init__(parent)

        self.setMaximumWidth(200)
        self.setDragEnabled(True)

        self._populate_blocks()

    def _populate_blocks(self) -> None:
        """Populate palette with available blocks."""
        blocks = {
            "Navigation": [
                ("Open URL", "OpenURLBlock"),
                ("Go Back", "BackBlock"),
                ("Go Forward", "ForwardBlock"),
                ("Refresh", "RefreshBlock"),
                ("New Tab", "NewTabBlock"),
                ("Close Tab", "CloseTabBlock"),
            ],
            "Actions": [
                ("Click", "ClickBlock"),
                ("Type Text", "TypeTextBlock"),
                ("Fill", "FillBlock"),
                ("Select", "SelectDropdownBlock"),
                ("Hover", "HoverBlock"),
                ("Scroll", "ScrollBlock"),
                ("Screenshot", "ScreenshotBlock"),
            ],
            "Wait": [
                ("Wait", "WaitBlock"),
                ("Wait Element", "WaitForElementBlock"),
                ("Wait Navigation", "WaitForNavigationBlock"),
                ("Wait Selector", "WaitForSelectorBlock"),
            ],
            "Data": [
                ("Extract Text", "ExtractTextBlock"),
                ("Extract Attr", "ExtractAttributeBlock"),
                ("Set Variable", "SetVariableBlock"),
                ("Get Variable", "GetVariableBlock"),
                ("Extract Multiple", "ExtractMultipleBlock"),
            ],
            "Control Flow": [
                ("If Condition", "IfBlock"),
                ("Loop", "LoopBlock"),
                ("Switch", "SwitchBlock"),
                ("Break", "BreakBlock"),
                ("Continue", "ContinueBlock"),
            ],
        }

        for category, block_list in blocks.items():
            # Add category header
            category_item = QListWidgetItem(f"--- {category} ---")
            category_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.addItem(category_item)

            # Add blocks
            for display_name, block_class_name in block_list:
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, block_class_name)
                self.addItem(item)

    def startDrag(self, supportedActions):
        """Start drag operation."""
        item = self.currentItem()
        if item:
            block_type = item.data(Qt.ItemDataRole.UserRole)
            if block_type:
                self.block_requested.emit(block_type)


class NodeEditor(QWidget):
    """Main node editor widget."""

    workflow_changed = pyqtSignal()
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(object)  # ExecutionResult

    def __init__(self, parent=None) -> None:
        """Initialize node editor."""
        super().__init__(parent)

        # Core components
        self.scene = NodeScene()
        self.executor: Optional[WorkflowExecutor] = None
        self.serializer = WorkflowSerializer()

        # State
        self.current_file: Optional[Path] = None
        self.is_executing = False

        # UI
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.btn_new = QPushButton("New")
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        self.btn_execute = QPushButton("Execute")
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)

        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_open)
        toolbar_layout.addWidget(self.btn_save)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_execute)
        toolbar_layout.addWidget(self.btn_stop)

        layout.addLayout(toolbar_layout)

        # Main content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Block palette
        self.palette = BlockPalette()
        splitter.addWidget(self.palette)

        # Canvas (use existing CanvasView from GUI)
        # For now, create a simple placeholder
        from PyQt6.QtWidgets import QGraphicsView

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints() | self.view.RenderHint.Antialiasing)
        splitter.addWidget(self.view)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # Status bar
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)

        layout.addLayout(status_layout)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self.btn_new.clicked.connect(self.new_workflow)
        self.btn_open.clicked.connect(self.open_workflow)
        self.btn_save.clicked.connect(self.save_workflow)
        self.btn_execute.clicked.connect(self.execute_workflow)
        self.btn_stop.clicked.connect(self.stop_execution)

        self.palette.block_requested.connect(self.add_block)

        self.scene.node_added.connect(lambda: self.workflow_changed.emit())
        self.scene.node_removed.connect(lambda: self.workflow_changed.emit())
        self.scene.connection_added.connect(lambda: self.workflow_changed.emit())

    def add_block(self, block_class_name: str) -> None:
        """Add block to scene.

        Args:
            block_class_name: Name of block class to add
        """
        try:
            # Get block class from globals
            block_class = globals().get(block_class_name)
            if not block_class:
                logger.error(f"Block class not found: {block_class_name}")
                return

            # Create block instance
            block = block_class()

            # Add to scene at center
            center = self.view.viewport().rect().center()
            scene_pos = self.view.mapToScene(center)
            block.graphics_node.setPos(scene_pos.x(), scene_pos.y())

            self.scene.add_node(block.graphics_node)

            logger.info(f"Added block: {block.title}")

        except Exception as e:
            logger.error(f"Failed to add block: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add block: {e}")

    def new_workflow(self) -> None:
        """Create new workflow."""
        if self.scene.has_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save current workflow?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_workflow()

        self.scene.clear()
        self.current_file = None
        self.status_label.setText("New workflow")

        logger.info("Created new workflow")

    def open_workflow(self) -> None:
        """Open workflow from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Workflow", "", "Workflow Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            blocks, connections_data = self.serializer.load_from_file(Path(file_path))

            self.scene.clear()

            # Add blocks
            for block in blocks:
                self.scene.add_node(block.graphics_node)

            # TODO: Create connections from connections_data
            # This requires matching block IDs to recreate connections

            self.current_file = Path(file_path)
            self.status_label.setText(f"Opened: {file_path}")

            logger.info(f"Opened workflow: {file_path}")

        except Exception as e:
            logger.error(f"Failed to open workflow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open workflow: {e}")

    def save_workflow(self) -> None:
        """Save workflow to file."""
        if not self.current_file:
            self.save_workflow_as()
            return

        try:
            blocks = self._get_all_blocks()
            connections = self.scene.get_connections()

            self.serializer.save_to_file(self.current_file, blocks, connections)

            self.status_label.setText(f"Saved: {self.current_file}")
            logger.info(f"Saved workflow: {self.current_file}")

        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save workflow: {e}")

    def save_workflow_as(self) -> None:
        """Save workflow to new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Workflow As", "", "Workflow Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        self.current_file = Path(file_path)
        self.save_workflow()

    async def execute_workflow(self) -> None:
        """Execute workflow."""
        if self.is_executing:
            QMessageBox.warning(self, "Warning", "Workflow is already executing")
            return

        try:
            blocks = self._get_all_blocks()
            connections = self.scene.get_connections()

            if not blocks:
                QMessageBox.warning(self, "Warning", "No blocks to execute")
                return

            # Create executor
            self.executor = WorkflowExecutor(blocks, connections)

            # Get browser instance (from context or create new)
            # For now, this is a placeholder
            browser = None  # TODO: Get browser from main app

            # Update UI
            self.is_executing = True
            self.btn_execute.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.status_label.setText("Executing...")

            self.execution_started.emit()

            # Execute
            result = await self.executor.execute(browser)

            # Update UI
            self.is_executing = False
            self.btn_execute.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.progress_bar.setVisible(False)

            if result.status == ExecutionStatus.COMPLETED:
                self.status_label.setText("Execution completed")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Workflow executed successfully\n\n"
                    f"Executed blocks: {result.executed_blocks}/{result.total_blocks}",
                )
            elif result.status == ExecutionStatus.FAILED:
                self.status_label.setText("Execution failed")
                error_text = "\n".join([e.get("error", "") for e in result.errors])
                QMessageBox.critical(
                    self, "Error", f"Workflow execution failed:\n\n{error_text}"
                )

            self.execution_finished.emit(result)

            logger.info(f"Workflow execution finished: {result.status.value}")

        except Exception as e:
            self.is_executing = False
            self.btn_execute.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.status_label.setText("Execution error")

            logger.error(f"Workflow execution error: {e}")
            QMessageBox.critical(self, "Error", f"Execution error: {e}")

    def stop_execution(self) -> None:
        """Stop workflow execution."""
        if self.executor:
            self.executor.cancel()
            self.status_label.setText("Execution cancelled")
            logger.info("Workflow execution cancelled")

    def _get_all_blocks(self) -> List[BaseBlock]:
        """Get all blocks from scene.

        Returns:
            List of blocks
        """
        blocks = []
        for item in self.scene.items():
            if hasattr(item, "block"):
                blocks.append(item.block)
        return blocks

    def _update_progress(self) -> None:
        """Update progress bar during execution."""
        if self.executor:
            progress = self.executor.get_progress()
            self.progress_bar.setValue(int(progress))
