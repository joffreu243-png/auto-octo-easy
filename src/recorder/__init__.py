"""
Action recorder module for OctoMaster Pro.

Provides functionality to record user actions in the browser,
analyze patterns, generate selectors, and export to various formats.
"""

from src.recorder.recorder import Recorder
from src.recorder.types import (
    RecordedAction,
    RecordingSession,
    EventType,
    ActionType,
    SelectorType,
    Selector,
    ElementInfo,
)
from src.recorder.selector_generator import SelectorGenerator
from src.recorder.action_analyzer import ActionAnalyzer
from src.recorder.script_generator import ScriptGenerator
from src.recorder.optimizer import ActionOptimizer
from src.recorder.event_listener import EventListener

__all__ = [
    # Main recorder
    "Recorder",
    # Types
    "RecordedAction",
    "RecordingSession",
    "EventType",
    "ActionType",
    "SelectorType",
    "Selector",
    "ElementInfo",
    # Components
    "SelectorGenerator",
    "ActionAnalyzer",
    "ScriptGenerator",
    "ActionOptimizer",
    "EventListener",
]
