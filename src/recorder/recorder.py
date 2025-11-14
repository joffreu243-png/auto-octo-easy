"""
Action recorder for capturing browser interactions.

This module records user actions and converts them into workflow nodes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from loguru import logger

from src.nodes.node import Node, NodeType
from src.core.exceptions import RecorderError


@dataclass
class RecordedAction:
    """Recorded action data."""

    action_type: str
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    timestamp: datetime = datetime.now()

    def to_node(self) -> Node:
        """
        Convert recorded action to workflow node.

        Returns:
            Node representing this action
        """
        node_type_map = {
            "navigate": NodeType.NAVIGATE,
            "click": NodeType.CLICK,
            "type": NodeType.TYPE,
            "wait": NodeType.WAIT,
        }

        node_type = node_type_map.get(self.action_type, NodeType.CLICK)
        node = Node(type=node_type)

        if self.selector:
            node.set_parameter("selector", self.selector)
        if self.value:
            node.set_parameter("value", self.value)
        if self.url:
            node.set_parameter("url", self.url)

        return node


class ActionRecorder:
    """
    Action recorder for capturing browser interactions.

    Records user actions and converts them into workflow nodes.
    """

    def __init__(self) -> None:
        """Initialize action recorder."""
        self.is_recording = False
        self.actions: List[RecordedAction] = []
        self.start_time: Optional[datetime] = None

        logger.debug("Action recorder initialized")

    def start_recording(self) -> None:
        """Start recording actions."""
        if self.is_recording:
            logger.warning("Already recording")
            return

        self.is_recording = True
        self.actions.clear()
        self.start_time = datetime.now()

        logger.info("Started recording")

    def stop_recording(self) -> None:
        """Stop recording actions."""
        if not self.is_recording:
            logger.warning("Not currently recording")
            return

        self.is_recording = False
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        logger.info(f"Stopped recording. Captured {len(self.actions)} actions in {duration:.2f}s")

    def record_action(
        self,
        action_type: str,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Record an action.

        Args:
            action_type: Type of action (navigate, click, type, etc.)
            selector: CSS selector for element
            value: Value for action (text to type, etc.)
            url: URL for navigation actions
        """
        if not self.is_recording:
            return

        action = RecordedAction(
            action_type=action_type,
            selector=selector,
            value=value,
            url=url,
        )

        self.actions.append(action)
        logger.debug(f"Recorded action: {action_type}")

    def get_actions(self) -> List[RecordedAction]:
        """
        Get recorded actions.

        Returns:
            List of recorded actions
        """
        return self.actions.copy()

    def convert_to_workflow(self) -> List[Node]:
        """
        Convert recorded actions to workflow nodes.

        Returns:
            List of workflow nodes
        """
        nodes = [action.to_node() for action in self.actions]
        logger.info(f"Converted {len(self.actions)} actions to {len(nodes)} nodes")
        return nodes

    def clear(self) -> None:
        """Clear recorded actions."""
        self.actions.clear()
        logger.debug("Cleared recorded actions")
