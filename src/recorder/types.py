"""
Type definitions for recorder module.

Defines action types, event types, and data models for recording.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


class EventType(Enum):
    """Browser event types."""

    CLICK = "click"
    DOUBLE_CLICK = "dblclick"
    RIGHT_CLICK = "contextmenu"
    KEYDOWN = "keydown"
    KEYUP = "keyup"
    INPUT = "input"
    CHANGE = "change"
    SUBMIT = "submit"
    FOCUS = "focus"
    BLUR = "blur"
    HOVER = "mouseover"
    SCROLL = "scroll"
    NAVIGATION = "navigation"
    WAIT = "wait"


class ActionType(Enum):
    """Recorded action types."""

    NAVIGATE = "navigate"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE_TEXT = "type_text"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    HOVER = "hover"
    SCROLL = "scroll"
    WAIT = "wait"
    WAIT_FOR_ELEMENT = "wait_for_element"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    CUSTOM = "custom"


class SelectorType(Enum):
    """Selector strategy types."""

    ID = "id"
    CLASS = "class"
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    PLACEHOLDER = "placeholder"
    ARIA_LABEL = "aria_label"
    DATA_TESTID = "data_testid"
    DATA_QA = "data_qa"
    NAME = "name"
    ROLE = "role"


@dataclass
class Selector:
    """Element selector with metadata."""

    type: SelectorType
    value: str
    score: float = 0.0  # Quality score (0-100)
    is_unique: bool = False
    is_stable: bool = True  # Likely to remain stable across sessions
    fallback: Optional["Selector"] = None

    def to_playwright(self) -> str:
        """Convert to Playwright selector format.

        Returns:
            Playwright selector string
        """
        if self.type == SelectorType.ID:
            return f"#{self.value}"
        elif self.type == SelectorType.CLASS:
            return f".{self.value}"
        elif self.type == SelectorType.CSS:
            return self.value
        elif self.type == SelectorType.XPATH:
            return f"xpath={self.value}"
        elif self.type == SelectorType.TEXT:
            return f"text={self.value}"
        elif self.type == SelectorType.PLACEHOLDER:
            return f"[placeholder='{self.value}']"
        elif self.type == SelectorType.ARIA_LABEL:
            return f"[aria-label='{self.value}']"
        elif self.type == SelectorType.DATA_TESTID:
            return f"[data-testid='{self.value}']"
        elif self.type == SelectorType.DATA_QA:
            return f"[data-qa='{self.value}']"
        elif self.type == SelectorType.NAME:
            return f"[name='{self.value}']"
        elif self.type == SelectorType.ROLE:
            return f"role={self.value}"
        return self.value


@dataclass
class ElementInfo:
    """Information about DOM element."""

    tag_name: str
    id: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    name: Optional[str] = None
    placeholder: Optional[str] = None
    aria_label: Optional[str] = None
    data_testid: Optional[str] = None
    data_qa: Optional[str] = None
    role: Optional[str] = None
    text: Optional[str] = None
    value: Optional[str] = None
    type: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    xpath: Optional[str] = None
    css_path: Optional[str] = None
    parent_info: Optional["ElementInfo"] = None


@dataclass
class RecordedAction:
    """Single recorded action."""

    type: ActionType
    timestamp: datetime
    element: Optional[ElementInfo] = None
    selectors: List[Selector] = field(default_factory=list)
    best_selector: Optional[Selector] = None
    value: Optional[str] = None  # For input/fill actions
    url: Optional[str] = None  # For navigation
    position: Optional[Dict[str, int]] = None  # x, y coordinates
    key: Optional[str] = None  # For keyboard events
    modifiers: List[str] = field(default_factory=list)  # Ctrl, Shift, Alt
    wait_time: Optional[float] = None  # For wait actions
    screenshot_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Action as dictionary
        """
        return {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "element": self._element_to_dict() if self.element else None,
            "selectors": [
                {"type": s.type.value, "value": s.value, "score": s.score}
                for s in self.selectors
            ],
            "best_selector": (
                {
                    "type": self.best_selector.type.value,
                    "value": self.best_selector.value,
                    "score": self.best_selector.score,
                }
                if self.best_selector
                else None
            ),
            "value": self.value,
            "url": self.url,
            "position": self.position,
            "key": self.key,
            "modifiers": self.modifiers,
            "wait_time": self.wait_time,
            "screenshot_path": self.screenshot_path,
            "metadata": self.metadata,
        }

    def _element_to_dict(self) -> Dict[str, Any]:
        """Convert element info to dictionary.

        Returns:
            Element as dictionary
        """
        if not self.element:
            return {}

        return {
            "tag_name": self.element.tag_name,
            "id": self.element.id,
            "classes": self.element.classes,
            "name": self.element.name,
            "placeholder": self.element.placeholder,
            "aria_label": self.element.aria_label,
            "data_testid": self.element.data_testid,
            "text": self.element.text,
            "value": self.element.value,
            "type": self.element.type,
            "href": self.element.href,
        }


@dataclass
class RecordingSession:
    """Complete recording session."""

    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    actions: List[RecordedAction] = field(default_factory=list)
    start_url: Optional[str] = None
    end_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_action(self, action: RecordedAction) -> None:
        """Add action to session.

        Args:
            action: Recorded action
        """
        self.actions.append(action)

    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds.

        Returns:
            Duration in seconds or None if not ended
        """
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Session as dictionary
        """
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "actions": [action.to_dict() for action in self.actions],
            "start_url": self.start_url,
            "end_url": self.end_url,
            "duration": self.get_duration(),
            "metadata": self.metadata,
        }


@dataclass
class OptimizedAction:
    """Optimized action after analysis."""

    original_actions: List[RecordedAction]
    type: ActionType
    selector: Selector
    value: Optional[str] = None
    is_loop: bool = False
    loop_count: Optional[int] = None
    is_conditional: bool = False
    condition: Optional[str] = None
    wait_before: Optional[float] = None
    wait_after: Optional[float] = None
    description: str = ""


@dataclass
class ActionPattern:
    """Detected pattern in actions."""

    type: str  # loop, condition, sequence
    actions: List[RecordedAction]
    confidence: float  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)
