"""
Node editor for visual workflow creation.

This module provides the core node editor functionality for creating and
managing visual workflows.
"""

from typing import Optional
from pathlib import Path
import json
from loguru import logger

from src.nodes.node import Node, NodeType
from src.nodes.connection import Connection
from src.core.exceptions import WorkflowError


class NodeEditor:
    """
    Visual node editor for workflow creation.

    Manages nodes, connections, and workflow state.
    """

    def __init__(self) -> None:
        """Initialize node editor."""
        self.nodes: dict[str, Node] = {}
        self.connections: dict[str, Connection] = {}
        self.is_modified = False

        logger.debug("Node editor initialized")

    def add_node(self, node: Node) -> bool:
        """
        Add a node to the workflow.

        Args:
            node: Node to add

        Returns:
            True if added successfully, False if node ID already exists
        """
        if node.id in self.nodes:
            logger.warning(f"Node with ID {node.id} already exists")
            return False

        self.nodes[node.id] = node
        self.is_modified = True
        logger.debug(f"Added node: {node.type.value} ({node.id})")
        return True

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the workflow.

        Args:
            node_id: ID of node to remove

        Returns:
            True if removed successfully, False if node not found
        """
        if node_id not in self.nodes:
            logger.warning(f"Node {node_id} not found")
            return False

        # Remove all connections to/from this node
        connections_to_remove = [
            conn_id
            for conn_id, conn in self.connections.items()
            if conn.source_node_id == node_id or conn.target_node_id == node_id
        ]

        for conn_id in connections_to_remove:
            self.remove_connection(conn_id)

        del self.nodes[node_id]
        self.is_modified = True
        logger.debug(f"Removed node: {node_id}")
        return True

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node or None if not found
        """
        return self.nodes.get(node_id)

    def add_connection(self, connection: Connection) -> bool:
        """
        Add a connection between nodes.

        Args:
            connection: Connection to add

        Returns:
            True if added successfully, False otherwise

        Raises:
            WorkflowError: If connection is invalid
        """
        # Validate nodes exist
        if connection.source_node_id not in self.nodes:
            raise WorkflowError(f"Source node not found: {connection.source_node_id}")
        if connection.target_node_id not in self.nodes:
            raise WorkflowError(f"Target node not found: {connection.target_node_id}")

        # Add connection
        self.connections[connection.id] = connection

        # Update node connections
        source_node = self.nodes[connection.source_node_id]
        target_node = self.nodes[connection.target_node_id]

        source_node.add_output(connection.target_node_id)
        target_node.add_input(connection.source_node_id)

        self.is_modified = True
        logger.debug(f"Added connection: {connection.source_node_id} -> {connection.target_node_id}")
        return True

    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection.

        Args:
            connection_id: Connection ID

        Returns:
            True if removed successfully, False if not found
        """
        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return False

        connection = self.connections[connection_id]

        # Update node connections
        if connection.source_node_id in self.nodes:
            self.nodes[connection.source_node_id].remove_output(connection.target_node_id)
        if connection.target_node_id in self.nodes:
            self.nodes[connection.target_node_id].remove_input(connection.source_node_id)

        del self.connections[connection_id]
        self.is_modified = True
        logger.debug(f"Removed connection: {connection_id}")
        return True

    def clear(self) -> None:
        """Clear all nodes and connections."""
        self.nodes.clear()
        self.connections.clear()
        self.is_modified = False
        logger.debug("Editor cleared")

    def save_to_file(self, file_path: Path) -> None:
        """
        Save workflow to file.

        Args:
            file_path: Path to save file

        Raises:
            WorkflowError: If save fails
        """
        try:
            workflow_data = {
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "connections": [conn.to_dict() for conn in self.connections.values()],
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(workflow_data, f, indent=2)

            self.is_modified = False
            logger.info(f"Workflow saved to {file_path}")

        except Exception as e:
            raise WorkflowError(f"Failed to save workflow: {e}") from e

    def load_from_file(self, file_path: Path) -> None:
        """
        Load workflow from file.

        Args:
            file_path: Path to load file

        Raises:
            WorkflowError: If load fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)

            self.clear()

            # Load nodes
            for node_data in workflow_data.get("nodes", []):
                node = Node.from_dict(node_data)
                self.add_node(node)

            # Load connections
            for conn_data in workflow_data.get("connections", []):
                connection = Connection.from_dict(conn_data)
                self.add_connection(connection)

            self.is_modified = False
            logger.info(f"Workflow loaded from {file_path}")

        except Exception as e:
            raise WorkflowError(f"Failed to load workflow: {e}") from e

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate workflow.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        # Check for at least one node
        if not self.nodes:
            errors.append("Workflow must contain at least one node")
            return False, errors

        # Check for cycles
        # TODO: Implement cycle detection

        # Check for unreachable nodes
        # TODO: Implement reachability check

        is_valid = len(errors) == 0
        return is_valid, errors
