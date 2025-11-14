"""
Graphics scene for node editor.

Manages nodes and connections in the visual editor.
"""

from typing import List, Optional
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QColor
from loguru import logger


class NodeScene(QGraphicsScene):
    """Graphics scene for node editor."""

    node_added = pyqtSignal(object)  # Emits node
    node_removed = pyqtSignal(object)  # Emits node
    connection_added = pyqtSignal(object)  # Emits connection
    connection_removed = pyqtSignal(object)  # Emits connection
    selection_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        """Initialize node scene."""
        super().__init__(parent)
        self.setSceneRect(-5000, -5000, 10000, 10000)

        # Scene configuration
        self.grid_size = 20
        self.grid_squares = 5

        self._nodes = []
        self._connections = []

        # Connect selection signal
        self.selectionChanged.connect(self._on_selection_changed)

    def add_node(self, node) -> None:
        """Add node to scene.

        Args:
            node: Node to add
        """
        self.addItem(node)
        self._nodes.append(node)
        self.node_added.emit(node)
        logger.info(f"Node added: {node.title}")

    def remove_node(self, node) -> None:
        """Remove node from scene.

        Args:
            node: Node to remove
        """
        # Remove all connections
        connections_to_remove = []
        for conn in self._connections:
            if conn.start_socket.node == node or conn.end_socket.node == node:
                connections_to_remove.append(conn)

        for conn in connections_to_remove:
            self.remove_connection(conn)

        # Remove node
        self.removeItem(node)
        if node in self._nodes:
            self._nodes.remove(node)

        self.node_removed.emit(node)
        logger.info(f"Node removed: {node.title}")

    def add_connection(self, connection) -> None:
        """Add connection to scene.

        Args:
            connection: Connection to add
        """
        self.addItem(connection)
        self._connections.append(connection)
        self.connection_added.emit(connection)
        logger.debug("Connection added")

    def remove_connection(self, connection) -> None:
        """Remove connection from scene.

        Args:
            connection: Connection to remove
        """
        self.removeItem(connection)
        if connection in self._connections:
            self._connections.remove(connection)

        self.connection_removed.emit(connection)
        logger.debug("Connection removed")

    def get_nodes(self) -> List:
        """Get all nodes in scene.

        Returns:
            List of nodes
        """
        return self._nodes.copy()

    def get_connections(self) -> List:
        """Get all connections in scene.

        Returns:
            List of connections
        """
        return self._connections.copy()

    def clear_scene(self) -> None:
        """Clear all nodes and connections."""
        # Remove all connections
        for conn in self._connections.copy():
            self.remove_connection(conn)

        # Remove all nodes
        for node in self._nodes.copy():
            self.remove_node(node)

        logger.info("Scene cleared")

    def _on_selection_changed(self) -> None:
        """Handle selection change."""
        self.selection_changed.emit()

    def get_selected_nodes(self) -> List:
        """Get selected nodes.

        Returns:
            List of selected nodes
        """
        return [item for item in self.selectedItems() if item in self._nodes]

    def delete_selected(self) -> None:
        """Delete selected items."""
        for item in self.selectedItems():
            if item in self._nodes:
                self.remove_node(item)
            elif item in self._connections:
                self.remove_connection(item)
