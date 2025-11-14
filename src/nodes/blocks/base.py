"""
Base block class for all workflow blocks.

Provides common functionality for all block types.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from loguru import logger

from src.nodes.graphics_node import GraphicsNode


class BaseBlock(ABC):
    """Base class for all workflow blocks."""

    def __init__(
        self,
        title: str,
        block_type: str = "default",
        num_inputs: int = 1,
        num_outputs: int = 1,
    ) -> None:
        """Initialize base block.

        Args:
            title: Block title
            block_type: Block type for color coding
            num_inputs: Number of input sockets
            num_outputs: Number of output sockets
        """
        self.title = title
        self.block_type = block_type
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        # Parameters
        self.params: Dict[str, Any] = {}

        # Graphics node
        self.graphics_node = GraphicsNode(title, block_type)

        # Add sockets
        for i in range(num_inputs):
            self.graphics_node.add_input_socket(i)

        for i in range(num_outputs):
            self.graphics_node.add_output_socket(i)

        self.graphics_node.update_size()

        # Execution state
        self._executed = False
        self._result: Optional[Any] = None
        self._error: Optional[str] = None

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute block logic.

        Args:
            context: Execution context with browser, variables, etc.

        Returns:
            Execution result
        """
        pass

    def set_param(self, name: str, value: Any) -> None:
        """Set parameter value.

        Args:
            name: Parameter name
            value: Parameter value
        """
        self.params[name] = value
        self._update_params_display()

    def get_param(self, name: str, default: Any = None) -> Any:
        """Get parameter value.

        Args:
            name: Parameter name
            default: Default value if not found

        Returns:
            Parameter value
        """
        return self.params.get(name, default)

    def _update_params_display(self) -> None:
        """Update parameter display on node."""
        if not self.params:
            self.graphics_node.set_params_text("")
            return

        # Create short param description
        param_text = "\n".join(
            f"{k}: {str(v)[:20]}..." if len(str(v)) > 20 else f"{k}: {v}"
            for k, v in list(self.params.items())[:3]
        )

        self.graphics_node.set_params_text(param_text)

    def serialize(self) -> Dict[str, Any]:
        """Serialize block to dictionary.

        Returns:
            Serialized block data
        """
        return {
            "title": self.title,
            "block_type": self.block_type,
            "params": self.params,
            "position": {
                "x": self.graphics_node.pos().x(),
                "y": self.graphics_node.pos().y(),
            },
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize block from dictionary.

        Args:
            data: Serialized block data
        """
        self.params = data.get("params", {})
        self._update_params_display()

        if "position" in data:
            pos = data["position"]
            self.graphics_node.setPos(pos["x"], pos["y"])

    def reset_execution(self) -> None:
        """Reset execution state."""
        self._executed = False
        self._result = None
        self._error = None

    @property
    def executed(self) -> bool:
        """Check if block was executed."""
        return self._executed

    @property
    def has_error(self) -> bool:
        """Check if block has error."""
        return self._error is not None

    def get_error(self) -> Optional[str]:
        """Get execution error."""
        return self._error

    def get_result(self) -> Optional[Any]:
        """Get execution result."""
        return self._result
