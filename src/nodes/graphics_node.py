"""
Graphics node components for visual node editor.

Provides visual representation of nodes with sockets and connections.
"""

from typing import Optional, List
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QPainterPath,
)


class Socket(QGraphicsItem):
    """Socket (connection point) on a node."""

    def __init__(
        self,
        node: "GraphicsNode",
        index: int = 0,
        socket_type: str = "input",
        parent=None,
    ) -> None:
        """Initialize socket.

        Args:
            node: Parent node
            index: Socket index
            socket_type: Socket type ('input' or 'output')
            parent: Parent graphics item
        """
        super().__init__(parent)
        self.node = node
        self.index = index
        self.socket_type = socket_type
        self.radius = 8
        self.connection = None

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        # Colors
        self.color_default = QColor("#7F7F7F")
        self.color_connected = QColor("#00FF00")
        self.color_hover = QColor("#FFFF00")

        self._current_color = self.color_default

    def boundingRect(self) -> QRectF:
        """Get bounding rectangle."""
        return QRectF(
            -self.radius - 2,
            -self.radius - 2,
            2 * (self.radius + 2),
            2 * (self.radius + 2),
        )

    def paint(
        self, painter: QPainter, option, widget=None
    ) -> None:
        """Paint socket."""
        # Outer circle
        painter.setBrush(QBrush(self._current_color))
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

        # Inner circle
        painter.setBrush(QBrush(QColor("#1e1e1e")))
        painter.setPen(Qt.PenStyle.NoPen)
        inner_radius = self.radius - 3
        painter.drawEllipse(
            -inner_radius, -inner_radius, 2 * inner_radius, 2 * inner_radius
        )

    def set_connected(self, connected: bool) -> None:
        """Set socket connected state.

        Args:
            connected: Whether socket is connected
        """
        self._current_color = self.color_connected if connected else self.color_default
        self.update()

    def hoverEnterEvent(self, event) -> None:
        """Handle hover enter."""
        self._current_color = self.color_hover
        self.update()

    def hoverLeaveEvent(self, event) -> None:
        """Handle hover leave."""
        self._current_color = (
            self.color_connected if self.connection else self.color_default
        )
        self.update()


class GraphicsNode(QGraphicsItem):
    """Graphics node for visual workflow editor."""

    def __init__(
        self,
        title: str,
        node_type: str = "default",
        parent=None,
    ) -> None:
        """Initialize graphics node.

        Args:
            title: Node title
            node_type: Node type for color coding
            parent: Parent graphics item
        """
        super().__init__(parent)

        self.title = title
        self.node_type = node_type
        self.width = 180
        self.height = 100
        self.title_height = 30
        self.edge_size = 10
        self.edge_roundness = 10

        # Colors based on node type
        self.color_map = {
            "navigation": QColor("#4A90E2"),  # Blue
            "action": QColor("#50C878"),  # Green
            "wait": QColor("#F5A623"),  # Orange
            "data": QColor("#9013FE"),  # Purple
            "condition": QColor("#D0021B"),  # Red
            "default": QColor("#7F7F7F"),  # Gray
        }

        self.title_color = self.color_map.get(node_type, self.color_map["default"])
        self.bg_color = QColor("#2d2d30")
        self.border_color = QColor("#000000")
        self.selected_color = QColor("#FFA637")

        # Sockets
        self.input_sockets: List[Socket] = []
        self.output_sockets: List[Socket] = []

        # Flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setZValue(1)

        # Title text
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(QColor("#ffffff"))
        self.title_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_item.setPlainText(title)
        self.title_item.setPos(15, 5)
        self.title_item.setTextWidth(self.width - 30)

        # Parameters text
        self.params_item = QGraphicsTextItem(self)
        self.params_item.setDefaultTextColor(QColor("#cccccc"))
        self.params_item.setFont(QFont("Arial", 8))
        self.params_item.setPos(15, self.title_height + 5)

    def boundingRect(self) -> QRectF:
        """Get bounding rectangle."""
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(
        self, painter: QPainter, option, widget=None
    ) -> None:
        """Paint node."""
        # Title background
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(
            0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(
            self.width - self.edge_roundness,
            self.title_height - self.edge_roundness,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.title_color))
        painter.drawPath(path_title.simplified())

        # Content background
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(
            0,
            self.title_height,
            self.width,
            self.height - self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(
            self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.bg_color))
        painter.drawPath(path_content.simplified())

        # Outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_roundness, self.edge_roundness)
        if self.isSelected():
            painter.setPen(QPen(self.selected_color, 3))
        else:
            painter.setPen(QPen(self.border_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline)

    def add_input_socket(self, index: int = 0) -> Socket:
        """Add input socket.

        Args:
            index: Socket index

        Returns:
            Created socket
        """
        socket = Socket(self, index, "input", self)
        socket.setPos(0, self.title_height + 20 + index * 25)
        self.input_sockets.append(socket)
        return socket

    def add_output_socket(self, index: int = 0) -> Socket:
        """Add output socket.

        Args:
            index: Socket index

        Returns:
            Created socket
        """
        socket = Socket(self, index, "output", self)
        socket.setPos(self.width, self.title_height + 20 + index * 25)
        self.output_sockets.append(socket)
        return socket

    def set_params_text(self, text: str) -> None:
        """Set parameters text.

        Args:
            text: Parameters description
        """
        self.params_item.setPlainText(text)

    def update_size(self) -> None:
        """Update node size based on content."""
        # Calculate required height
        socket_count = max(len(self.input_sockets), len(self.output_sockets))
        min_height = self.title_height + 40 + socket_count * 25

        if self.height < min_height:
            self.height = min_height
            self.update()
