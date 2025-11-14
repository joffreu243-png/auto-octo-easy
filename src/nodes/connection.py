"""
Connection classes for node editor.

This module provides connection representations between nodes in the workflow.
"""

from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Connection:
    """
    Connection between two nodes.

    Represents a directed connection from one node's output to another node's input.
    """

    id: str
    source_node_id: str
    target_node_id: str

    def __init__(self, source_node_id: str, target_node_id: str, connection_id: str = "") -> None:
        """
        Initialize connection.

        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            connection_id: Optional connection ID
        """
        self.id = connection_id or str(uuid4())
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id

    def to_dict(self) -> dict:
        """Convert connection to dictionary."""
        return {
            "id": self.id,
            "source": self.source_node_id,
            "target": self.target_node_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Connection":
        """Create connection from dictionary."""
        return cls(
            source_node_id=data["source"],
            target_node_id=data["target"],
            connection_id=data.get("id", ""),
        )
