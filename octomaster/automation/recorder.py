"""
Action Recorder for OctoMaster Pro.

Records user actions in the browser and converts them to workflow blocks.
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from loguru import logger

from octomaster.core.block import Block, BlockType
from octomaster.core.workflow import Workflow


class RecordedAction:
    """Represents a recorded user action."""

    def __init__(
        self,
        action_type: str,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.action_type = action_type
        self.selector = selector
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_block(self) -> Block:
        """Convert recorded action to a workflow block."""
        block_type_map = {
            "navigate": BlockType.OPEN_URL,
            "click": BlockType.CLICK,
            "type": BlockType.TYPE_TEXT,
            "select": BlockType.SELECT,
            "hover": BlockType.HOVER,
            "scroll": BlockType.SCROLL,
        }

        block_type = block_type_map.get(self.action_type, BlockType.CLICK)
        block = Block(type=block_type)

        # Set parameters based on action type
        if self.action_type == "navigate":
            block.set_parameter("url", self.value)

        elif self.action_type in ("click", "hover"):
            block.set_parameter("selector", self.selector)

        elif self.action_type == "type":
            block.set_parameter("selector", self.selector)
            block.set_parameter("text", self.value)

        elif self.action_type == "select":
            block.set_parameter("selector", self.selector)
            block.set_parameter("value", self.value)

        return block

    def __repr__(self) -> str:
        return f"RecordedAction(type={self.action_type}, selector={self.selector}, value={self.value})"


class Recorder:
    """
    Records user actions and converts them to workflow.
    """

    def __init__(self):
        self.is_recording = False
        self.recorded_actions: List[RecordedAction] = []
        self.start_time: Optional[datetime] = None
        self.callbacks: Dict[str, List[Callable]] = {
            "action_recorded": [],
            "recording_started": [],
            "recording_stopped": [],
        }

    def start(self):
        """Start recording."""
        self.is_recording = True
        self.recorded_actions = []
        self.start_time = datetime.now()
        logger.info("Recording started")

        self._trigger_callbacks("recording_started")

    def stop(self):
        """Stop recording."""
        self.is_recording = False
        logger.info(f"Recording stopped. Recorded {len(self.recorded_actions)} actions")

        self._trigger_callbacks("recording_stopped")

    def record_action(
        self,
        action_type: str,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a user action."""
        if not self.is_recording:
            return

        action = RecordedAction(
            action_type=action_type, selector=selector, value=value, metadata=metadata
        )

        self.recorded_actions.append(action)
        logger.debug(f"Action recorded: {action}")

        self._trigger_callbacks("action_recorded", action)

    def record_navigation(self, url: str):
        """Record navigation to URL."""
        self.record_action("navigate", value=url)

    def record_click(self, selector: str, button: str = "left"):
        """Record click action."""
        self.record_action("click", selector=selector, metadata={"button": button})

    def record_type(self, selector: str, text: str):
        """Record text input."""
        self.record_action("type", selector=selector, value=text)

    def record_select(self, selector: str, value: str):
        """Record select/dropdown change."""
        self.record_action("select", selector=selector, value=value)

    def record_hover(self, selector: str):
        """Record hover action."""
        self.record_action("hover", selector=selector)

    def record_scroll(self, x: int, y: int):
        """Record scroll action."""
        self.record_action("scroll", metadata={"x": x, "y": y})

    def to_workflow(self, name: str = "Recorded Workflow") -> Workflow:
        """Convert recorded actions to workflow."""
        workflow = Workflow(name=name)
        workflow.description = (
            f"Auto-generated from recording on {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Convert actions to blocks
        for action in self.recorded_actions:
            block = action.to_block()
            workflow.add_block(block)

        # Connect blocks sequentially
        for i in range(len(workflow.blocks) - 1):
            workflow.connect_blocks(workflow.blocks[i].id, workflow.blocks[i + 1].id)

        logger.info(f"Created workflow with {len(workflow.blocks)} blocks")
        return workflow

    def optimize(self):
        """Optimize recorded actions."""
        # TODO: Implement optimization
        # - Remove duplicate actions
        # - Detect loops
        # - Merge similar actions
        # - Remove unnecessary waits
        logger.info("Optimization not implemented yet")

    def add_callback(self, event: str, callback: Callable):
        """Add callback for events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str, *args, **kwargs):
        """Trigger callbacks for an event."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

    def clear(self):
        """Clear recorded actions."""
        self.recorded_actions = []
        logger.info("Recorded actions cleared")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of recording."""
        action_counts = {}
        for action in self.recorded_actions:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1

        return {
            "total_actions": len(self.recorded_actions),
            "action_types": action_counts,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "is_recording": self.is_recording,
        }

    def __repr__(self) -> str:
        return f"Recorder(recording={self.is_recording}, actions={len(self.recorded_actions)})"
