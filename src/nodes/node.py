"""
Node classes for visual workflow editor.

This module provides node representations for the visual workflow system.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from uuid import uuid4


class NodeType(str, Enum):
    """Node type enumeration."""

    # Navigation
    NAVIGATE = "navigate"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    RELOAD = "reload"

    # Interaction
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG_DROP = "drag_drop"

    # Waiting
    WAIT = "wait"
    WAIT_FOR_ELEMENT = "wait_for_element"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"

    # Data Extraction
    EXTRACT_TEXT = "extract_text"
    EXTRACT_ATTRIBUTE = "extract_attribute"
    EXTRACT_HTML = "extract_html"

    # Logic
    CONDITION = "condition"
    LOOP = "loop"
    BREAK = "break"
    CONTINUE = "continue"

    # Variables
    SET_VARIABLE = "set_variable"
    GET_VARIABLE = "get_variable"

    # Screenshot & Media
    SCREENSHOT = "screenshot"
    DOWNLOAD_FILE = "download_file"

    # Control
    START = "start"
    END = "end"


@dataclass
class Node:
    """
    Node representation in workflow.

    A node represents a single action or operation in the workflow.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    type: NodeType = NodeType.START
    name: str = ""
    description: str = ""
    x: float = 0.0
    y: float = 0.0
    parameters: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)  # Connected node IDs
    outputs: list[str] = field(default_factory=list)  # Connected node IDs

    def __post_init__(self) -> None:
        """Initialize after dataclass initialization."""
        if not self.name:
            self.name = self.type.value.replace("_", " ").title()

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Get parameter value.

        Args:
            key: Parameter key
            default: Default value if not found

        Returns:
            Parameter value or default
        """
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        """
        Set parameter value.

        Args:
            key: Parameter key
            value: Parameter value
        """
        self.parameters[key] = value

    def add_input(self, node_id: str) -> None:
        """
        Add input connection.

        Args:
            node_id: ID of input node
        """
        if node_id not in self.inputs:
            self.inputs.append(node_id)

    def add_output(self, node_id: str) -> None:
        """
        Add output connection.

        Args:
            node_id: ID of output node
        """
        if node_id not in self.outputs:
            self.outputs.append(node_id)

    def remove_input(self, node_id: str) -> None:
        """
        Remove input connection.

        Args:
            node_id: ID of input node
        """
        if node_id in self.inputs:
            self.inputs.remove(node_id)

    def remove_output(self, node_id: str) -> None:
        """
        Remove output connection.

        Args:
            node_id: ID of output node
        """
        if node_id in self.outputs:
            self.outputs.remove(node_id)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert node to dictionary.

        Returns:
            Node as dictionary
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "parameters": self.parameters,
            "inputs": self.inputs,
            "outputs": self.outputs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Node":
        """
        Create node from dictionary.

        Args:
            data: Node data

        Returns:
            Node instance
        """
        return cls(
            id=data.get("id", str(uuid4())),
            type=NodeType(data["type"]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            parameters=data.get("parameters", {}),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
        )
