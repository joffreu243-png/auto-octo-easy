"""
Connection graphics item for visual editor.

Draws bezier curves between blocks.
"""

from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainterPath, QPen, QColor, QPainter

from octomaster.core.workflow import Connection


class ConnectionGraphicsItem(QGraphicsPathItem):
    """
    Visual representation of a connection between two blocks.

    Draws a bezier curve from source block output to target block input.
    """

    def __init__(self, connection: Connection, source_item, target_item):
        super().__init__()

        self.connection = connection
        self.source_item = source_item
        self.target_item = target_item

        # Style
        pen = QPen(QColor(150, 150, 150), 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)

        # Z-order (behind blocks)
        self.setZValue(-1)

        # Make it selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Update path
        self.update_path()

    def update_path(self):
        """Update the connection path based on block positions."""
        # Get source and target positions
        source_pos = self.source_item.scenePos()
        target_pos = self.target_item.scenePos()

        # Output port is on the right side of source block
        start_x = source_pos.x() + self.source_item.width
        start_y = source_pos.y() + self.source_item.height / 2
        start = QPointF(start_x, start_y)

        # Input port is on the left side of target block
        end_x = target_pos.x()
        end_y = target_pos.y() + self.target_item.height / 2
        end = QPointF(end_x, end_y)

        # Create bezier curve path
        path = QPainterPath()
        path.moveTo(start)

        # Control points for smooth curve
        dx = abs(end.x() - start.x())
        ctrl_offset = min(dx * 0.5, 100)

        ctrl1 = QPointF(start.x() + ctrl_offset, start.y())
        ctrl2 = QPointF(end.x() - ctrl_offset, end.y())

        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)

    def paint(self, painter, option, widget=None):
        """Custom paint for selection highlight."""
        # Draw selection highlight if selected
        if self.isSelected():
            pen = QPen(QColor(100, 180, 255), 3)
            pen.setStyle(Qt.PenStyle.SolidLine)
            self.setPen(pen)
        else:
            pen = QPen(QColor(150, 150, 150), 2)
            self.setPen(pen)

        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        """Handle item changes."""
        # Update path when items move
        if change == QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
            self.update_path()

        return super().itemChange(change, value)

    def __repr__(self) -> str:
        return f"ConnectionGraphicsItem({self.connection.id[:8]})"
