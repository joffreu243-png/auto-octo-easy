"""
Graphics connection for node editor.

Visual representation of connections between nodes.
"""

from typing import Optional
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPainter


class GraphicsConnection(QGraphicsPathItem):
    """Graphics connection between two sockets."""

    def __init__(
        self,
        start_socket=None,
        end_socket=None,
        parent=None,
    ) -> None:
        """Initialize graphics connection.

        Args:
            start_socket: Starting socket
            end_socket: Ending socket
            parent: Parent graphics item
        """
        super().__init__(parent)

        self.start_socket = start_socket
        self.end_socket = end_socket

        # Visual properties
        self.color_default = QColor("#7F7F7F")
        self.color_selected = QColor("#FFA637")
        self.width = 3
        self.width_selected = 4

        self.setPen(QPen(self.color_default, self.width))
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)

        # Drag state
        self.dragging = False
        self.drag_start_pos = QPointF()
        self.drag_end_pos = QPointF()

        # Update path
        self.update_path()

    def update_path(self) -> None:
        """Update connection path."""
        # Get socket positions
        if self.start_socket:
            start_pos = self.start_socket.scenePos()
        else:
            start_pos = self.drag_start_pos

        if self.end_socket:
            end_pos = self.end_socket.scenePos()
        else:
            end_pos = self.drag_end_pos

        # Create bezier curve
        path = QPainterPath(start_pos)

        # Calculate control points for smooth curve
        dist = (end_pos.x() - start_pos.x()) * 0.5

        ctrl1 = QPointF(start_pos.x() + dist, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - dist, end_pos.y())

        path.cubicTo(ctrl1, ctrl2, end_pos)

        self.setPath(path)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        """Paint connection."""
        # Update pen based on selection
        if self.isSelected():
            self.setPen(QPen(self.color_selected, self.width_selected))
        else:
            self.setPen(QPen(self.color_default, self.width))

        super().paint(painter, option, widget)

    def set_dragging(self, dragging: bool, start_pos: QPointF = None, end_pos: QPointF = None) -> None:
        """Set dragging state.

        Args:
            dragging: Whether connection is being dragged
            start_pos: Drag start position
            end_pos: Drag end position
        """
        self.dragging = dragging

        if start_pos:
            self.drag_start_pos = start_pos
        if end_pos:
            self.drag_end_pos = end_pos

        self.update_path()
