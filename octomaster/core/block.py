"""
Block system for visual workflow builder.

Blocks are the building blocks (pun intended) of workflows in OctoMaster Pro.
Each block represents a single action or operation.
"""

from enum import Enum
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from uuid import uuid4


class BlockType(Enum):
    """Types of blocks available in the workflow builder."""

    # Navigation
    OPEN_URL = "open_url"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    REFRESH = "refresh"
    CLOSE_TAB = "close_tab"
    SWITCH_TAB = "switch_tab"

    # Actions
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    TYPE_TEXT = "type_text"
    CLEAR = "clear"
    SELECT = "select"
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    SCROLL = "scroll"

    # Waits
    WAIT_FOR_ELEMENT = "wait_for_element"
    WAIT_FOR_DISAPPEAR = "wait_for_disappear"
    WAIT_FOR_TEXT = "wait_for_text"
    WAIT_TIME = "wait_time"
    WAIT_FOR_LOAD = "wait_for_load"

    # Data Extraction
    GET_TEXT = "get_text"
    GET_ATTRIBUTE = "get_attribute"
    GET_HTML = "get_html"
    SCREENSHOT = "screenshot"
    GET_COOKIES = "get_cookies"

    # Conditions
    IF = "if"
    ELSE = "else"
    LOOP = "loop"
    FOR_EACH = "for_each"
    WHILE = "while"
    TRY_CATCH = "try_catch"

    # Data
    VARIABLE = "variable"
    LIST = "list"
    DICT = "dict"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    READ_CSV = "read_csv"
    WRITE_CSV = "write_csv"

    # Octo Browser
    CREATE_PROFILE = "create_profile"
    START_PROFILE = "start_profile"
    STOP_PROFILE = "stop_profile"
    DELETE_PROFILE = "delete_profile"
    GET_PROFILES = "get_profiles"

    # Integrations
    HTTP_REQUEST = "http_request"
    SEND_EMAIL = "send_email"
    SEND_TELEGRAM = "send_telegram"
    WEBHOOK = "webhook"


@dataclass
class BlockInput:
    """Input port for a block."""

    name: str
    type: str  # 'exec' for execution flow, 'data' for data
    label: str
    required: bool = True


@dataclass
class BlockOutput:
    """Output port for a block."""

    name: str
    type: str  # 'exec' for execution flow, 'data' for data
    label: str


@dataclass
class BlockParameter:
    """Parameter for block configuration."""

    name: str
    label: str
    type: str  # 'string', 'number', 'boolean', 'selector', etc.
    default: Any = None
    required: bool = False
    description: str = ""
    options: Optional[List[str]] = None  # For dropdown/select


@dataclass
class Block:
    """
    A block in the workflow.

    Blocks are the fundamental units of automation workflows.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    type: BlockType = BlockType.CLICK
    name: str = ""
    description: str = ""

    # Configuration
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Connections
    inputs: List[BlockInput] = field(default_factory=list)
    outputs: List[BlockOutput] = field(default_factory=list)

    # Position in visual editor
    x: int = 0
    y: int = 0

    # State
    enabled: bool = True
    breakpoint: bool = False

    # Metadata
    category: str = ""
    color: str = "#2196F3"  # Default blue
    icon: str = ""

    def __post_init__(self):
        """Initialize block after creation."""
        if not self.name:
            self.name = self.type.value.replace("_", " ").title()

        if not self.inputs:
            self.inputs = [BlockInput(name="in", type="exec", label="In")]

        if not self.outputs:
            self.outputs = [BlockOutput(name="out", type="exec", label="Out")]

        # Set category and color based on type
        self._set_category_and_color()

    def _set_category_and_color(self):
        """Set category and color based on block type."""
        navigation_blocks = {
            BlockType.OPEN_URL,
            BlockType.GO_BACK,
            BlockType.GO_FORWARD,
            BlockType.REFRESH,
        }
        action_blocks = {
            BlockType.CLICK,
            BlockType.TYPE_TEXT,
            BlockType.HOVER,
            BlockType.SCROLL,
        }
        wait_blocks = {
            BlockType.WAIT_FOR_ELEMENT,
            BlockType.WAIT_TIME,
            BlockType.WAIT_FOR_LOAD,
        }
        data_blocks = {BlockType.GET_TEXT, BlockType.GET_ATTRIBUTE, BlockType.SCREENSHOT}

        if self.type in navigation_blocks:
            self.category = "Navigation"
            self.color = "#2196F3"  # Blue
        elif self.type in action_blocks:
            self.category = "Actions"
            self.color = "#4CAF50"  # Green
        elif self.type in wait_blocks:
            self.category = "Waits"
            self.color = "#FFC107"  # Yellow
        elif self.type in data_blocks:
            self.category = "Data Extraction"
            self.color = "#FF9800"  # Orange

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get parameter value."""
        return self.parameters.get(name, default)

    def set_parameter(self, name: str, value: Any) -> None:
        """Set parameter value."""
        self.parameters[name] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "position": {"x": self.x, "y": self.y},
            "enabled": self.enabled,
            "breakpoint": self.breakpoint,
            "category": self.category,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create block from dictionary."""
        block_type = BlockType(data["type"])
        position = data.get("position", {})

        return cls(
            id=data.get("id", str(uuid4())),
            type=block_type,
            name=data.get("name", ""),
            description=data.get("description", ""),
            parameters=data.get("parameters", {}),
            x=position.get("x", 0),
            y=position.get("y", 0),
            enabled=data.get("enabled", True),
            breakpoint=data.get("breakpoint", False),
        )

    def clone(self) -> "Block":
        """Create a copy of this block with a new ID."""
        return Block(
            type=self.type,
            name=self.name,
            description=self.description,
            parameters=self.parameters.copy(),
            x=self.x + 20,  # Offset position
            y=self.y + 20,
            enabled=self.enabled,
            category=self.category,
            color=self.color,
        )

    def __repr__(self) -> str:
        return f"Block(id={self.id[:8]}, type={self.type.value}, name={self.name})"
