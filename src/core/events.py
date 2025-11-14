"""
Event system for OctoMaster Pro.

This module provides a comprehensive event bus system for decoupled communication
between components using the publish-subscribe pattern.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from enum import Enum
from loguru import logger


class EventType(str, Enum):
    """Event types enumeration."""

    # Application events
    APP_STARTED = "app.started"
    APP_STOPPED = "app.stopped"
    APP_ERROR = "app.error"

    # Workflow events
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_OPENED = "workflow.opened"
    WORKFLOW_SAVED = "workflow.saved"
    WORKFLOW_CLOSED = "workflow.closed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_STOPPED = "workflow.stopped"

    # Block events
    BLOCK_ADDED = "block.added"
    BLOCK_REMOVED = "block.removed"
    BLOCK_MODIFIED = "block.modified"
    BLOCK_CONNECTED = "block.connected"
    BLOCK_DISCONNECTED = "block.disconnected"
    BLOCK_STARTED = "block.started"
    BLOCK_COMPLETED = "block.completed"
    BLOCK_FAILED = "block.failed"

    # Browser events
    BROWSER_STARTED = "browser.started"
    BROWSER_STOPPED = "browser.stopped"
    BROWSER_NAVIGATED = "browser.navigated"
    BROWSER_PAGE_LOADED = "browser.page_loaded"
    BROWSER_ERROR = "browser.error"

    # Recorder events
    RECORDER_STARTED = "recorder.started"
    RECORDER_STOPPED = "recorder.stopped"
    RECORDER_ACTION_RECORDED = "recorder.action_recorded"

    # Plugin events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"

    # Scheduler events
    TASK_SCHEDULED = "task.scheduled"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # UI events
    UI_THEME_CHANGED = "ui.theme_changed"
    UI_PANEL_TOGGLED = "ui.panel_toggled"


@dataclass
class Event:
    """Event data class."""

    type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate event after initialization."""
        if isinstance(self.type, str):
            # Convert string to EventType if possible
            try:
                self.type = EventType(self.type)
            except ValueError:
                logger.warning(f"Unknown event type: {self.type}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get event data value.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set event data value.

        Args:
            key: Data key
            value: Data value
        """
        self.data[key] = value


EventCallback = Callable[[Event], None]


class EventBus:
    """
    Event bus for publish-subscribe pattern.

    Allows components to communicate without tight coupling.
    """

    def __init__(self) -> None:
        """Initialize event bus."""
        self._subscribers: dict[EventType, list[EventCallback]] = {}
        self._wildcard_subscribers: list[EventCallback] = []
        self._event_history: list[Event] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}")

    def subscribe_all(self, callback: EventCallback) -> None:
        """
        Subscribe to all events.

        Args:
            callback: Function to call for any event
        """
        self._wildcard_subscribers.append(callback)
        logger.debug("Subscribed to all events")

    def unsubscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from {event_type.value}")
            except ValueError:
                logger.warning(f"Callback not found for {event_type.value}")

    def unsubscribe_all(self, callback: EventCallback) -> None:
        """
        Unsubscribe from all events.

        Args:
            callback: Callback function to remove
        """
        try:
            self._wildcard_subscribers.remove(callback)
            logger.debug("Unsubscribed from all events")
        except ValueError:
            logger.warning("Callback not found in wildcard subscribers")

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        logger.debug(f"Publishing event: {event.type.value}")

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Call specific subscribers
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback for {event.type.value}: {e}")

        # Call wildcard subscribers
        for callback in self._wildcard_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in wildcard event callback: {e}")

    def emit(
        self,
        event_type: EventType,
        data: Optional[dict[str, Any]] = None,
        source: Optional[str] = None,
    ) -> None:
        """
        Emit an event (convenience method).

        Args:
            event_type: Type of event
            data: Event data
            source: Event source
        """
        event = Event(type=event_type, data=data or {}, source=source)
        self.publish(event)

    def clear_subscribers(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
        self._wildcard_subscribers.clear()
        logger.info("Cleared all event subscribers")

    def get_history(self, count: Optional[int] = None) -> list[Event]:
        """
        Get event history.

        Args:
            count: Number of recent events to return (None for all)

        Returns:
            List of events
        """
        if count is None:
            return self._event_history.copy()
        return self._event_history[-count:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
        logger.debug("Cleared event history")


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get global event bus instance.

    Returns:
        EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def emit_event(
    event_type: EventType,
    data: Optional[dict[str, Any]] = None,
    source: Optional[str] = None,
) -> None:
    """
    Emit an event to the global event bus.

    Args:
        event_type: Type of event
        data: Event data
        source: Event source
    """
    get_event_bus().emit(event_type, data, source)
