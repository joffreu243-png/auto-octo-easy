"""
Visual Editor widget - Node-based workflow builder.

This is the main canvas where users create workflows by connecting blocks.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QToolBar,
    QPushButton,
    QMenu,
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QContextMenuEvent,
    QWheelEvent,
)
from loguru import logger

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType


class BlockGraphicsItem(QGraphicsRectItem):
    """Graphical representation of a block in the visual editor."""

    def __init__(self, block: Block):
        super().__init__()
        self.block = block

        # Size
        self.width = 180
        self.height = 60

        # Setup
        self.setRect(0, 0, self.width, self.height)
        self.setPos(block.x, block.y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # Style
        color = QColor(block.color)
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(120), 2))

        # Text
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(block.name)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.text_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Center text
        text_width = self.text_item.boundingRect().width()
        text_height = self.text_item.boundingRect().height()
        self.text_item.setPos(
            (self.width - text_width) / 2, (self.height - text_height) / 2
        )

    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update block position
            new_pos = value
            self.block.x = int(new_pos.x())
            self.block.y = int(new_pos.y())

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.RightButton:
            # Show context menu
            pass
        super().mousePressEvent(event)


class VisualEditorScene(QGraphicsScene):
    """Custom scene for the visual editor."""

    block_added = pyqtSignal(Block)
    block_removed = pyqtSignal(str)
    connection_added = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor(45, 45, 48)))

        # Grid
        self.grid_size = 20
        self.draw_grid()

    def draw_grid(self):
        """Draw background grid."""
        # TODO: Implement grid drawing
        pass

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draw custom background."""
        super().drawBackground(painter, rect)

        # Draw grid
        painter.setPen(QPen(QColor(60, 60, 65), 1))

        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        # Vertical lines
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += self.grid_size

        # Horizontal lines
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += self.grid_size


class VisualEditorView(QGraphicsView):
    """Custom view for the visual editor with zoom and pan."""

    def __init__(self, scene: VisualEditorScene):
        super().__init__(scene)

        # Setup
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Pan
        self.panning = False
        self.pan_start = QPointF()

        # Zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        # Zoom in/out
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Check zoom limits
        new_zoom = self.zoom_factor * zoom_factor
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.scale(zoom_factor, zoom_factor)
            self.zoom_factor = new_zoom

    def mousePressEvent(self, event):
        """Handle mouse press for panning."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for panning."""
        if self.panning:
            delta = event.pos() - self.pan_start
            self.pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton and self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class VisualEditor(QWidget):
    """Visual workflow editor - main canvas for creating workflows."""

    workflow_changed = pyqtSignal(Workflow)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow = Workflow()
        self.block_items = {}  # block_id -> BlockGraphicsItem

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Add block button
        add_block_btn = QPushButton("➕ Add Block")
        add_block_btn.clicked.connect(self.show_add_block_menu)
        toolbar.addWidget(add_block_btn)

        toolbar.addSeparator()

        # Zoom controls
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(zoom_out_btn)

        zoom_fit_btn = QPushButton("⬜ Fit")
        zoom_fit_btn.clicked.connect(self.zoom_fit)
        toolbar.addWidget(zoom_fit_btn)

        toolbar.addSeparator()

        # Layout
        layout_btn = QPushButton("📐 Auto Layout")
        layout_btn.clicked.connect(self.auto_layout)
        toolbar.addWidget(layout_btn)

        layout.addWidget(toolbar)

        # Scene and view
        self.scene = VisualEditorScene()
        self.view = VisualEditorView(self.scene)
        layout.addWidget(self.view)

        # Connect signals
        self.scene.block_added.connect(self.on_block_added)
        self.scene.block_removed.connect(self.on_block_removed)

    def set_workflow(self, workflow: Workflow):
        """Set the current workflow."""
        self.workflow = workflow
        self.refresh()

    def refresh(self):
        """Refresh the view with current workflow."""
        # Clear scene
        self.scene.clear()
        self.block_items.clear()

        # Add blocks
        for block in self.workflow.blocks:
            self.add_block_to_scene(block)

        # TODO: Add connections

    def add_block_to_scene(self, block: Block):
        """Add a block to the scene."""
        item = BlockGraphicsItem(block)
        self.scene.addItem(item)
        self.block_items[block.id] = item

    def show_add_block_menu(self):
        """Show menu to add blocks."""
        menu = QMenu(self)

        # Navigation
        nav_menu = menu.addMenu("🧭 Navigation")
        nav_menu.addAction("Open URL", lambda: self.add_block(BlockType.OPEN_URL))
        nav_menu.addAction("Go Back", lambda: self.add_block(BlockType.GO_BACK))
        nav_menu.addAction("Refresh", lambda: self.add_block(BlockType.REFRESH))

        # Actions
        action_menu = menu.addMenu("⚡ Actions")
        action_menu.addAction("Click", lambda: self.add_block(BlockType.CLICK))
        action_menu.addAction("Type Text", lambda: self.add_block(BlockType.TYPE_TEXT))
        action_menu.addAction("Hover", lambda: self.add_block(BlockType.HOVER))
        action_menu.addAction("Scroll", lambda: self.add_block(BlockType.SCROLL))

        # Waits
        wait_menu = menu.addMenu("⏱️ Waits")
        wait_menu.addAction(
            "Wait for Element", lambda: self.add_block(BlockType.WAIT_FOR_ELEMENT)
        )
        wait_menu.addAction("Wait Time", lambda: self.add_block(BlockType.WAIT_TIME))

        # Data
        data_menu = menu.addMenu("📊 Data Extraction")
        data_menu.addAction("Get Text", lambda: self.add_block(BlockType.GET_TEXT))
        data_menu.addAction("Screenshot", lambda: self.add_block(BlockType.SCREENSHOT))

        menu.exec(self.mapToGlobal(self.sender().pos()))

    def add_block(self, block_type: BlockType):
        """Add a new block to the workflow."""
        block = Block(type=block_type)
        block.x = 100
        block.y = 100

        self.workflow.add_block(block)
        self.add_block_to_scene(block)

        self.workflow_changed.emit(self.workflow)
        logger.info(f"Added block: {block.name}")

    def zoom_in(self):
        """Zoom in the view."""
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out the view."""
        self.view.scale(1 / 1.15, 1 / 1.15)

    def zoom_fit(self):
        """Fit all items in view."""
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def auto_layout(self):
        """Auto-arrange blocks."""
        # TODO: Implement auto-layout algorithm
        logger.info("Auto-layout not implemented yet")

    def on_block_added(self, block: Block):
        """Handle block added."""
        pass

    def on_block_removed(self, block_id: str):
        """Handle block removed."""
        if block_id in self.block_items:
            item = self.block_items[block_id]
            self.scene.removeItem(item)
            del self.block_items[block_id]
