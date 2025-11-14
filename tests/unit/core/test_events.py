"""
Unit tests for event system.

Tests the EventBus, Event class, and event handling functionality.
"""

import pytest
from datetime import datetime
from src.core.events import (
    Event,
    EventType,
    EventBus,
    get_event_bus,
    emit_event,
)


class TestEventType:
    """Tests for EventType enum."""

    def test_app_events(self):
        """Test application event types exist."""
        assert EventType.APP_STARTED == "app.started"
        assert EventType.APP_STOPPED == "app.stopped"
        assert EventType.APP_ERROR == "app.error"

    def test_workflow_events(self):
        """Test workflow event types exist."""
        assert EventType.WORKFLOW_CREATED == "workflow.created"
        assert EventType.WORKFLOW_STARTED == "workflow.started"
        assert EventType.WORKFLOW_COMPLETED == "workflow.completed"
        assert EventType.WORKFLOW_FAILED == "workflow.failed"

    def test_block_events(self):
        """Test block event types exist."""
        assert EventType.BLOCK_ADDED == "block.added"
        assert EventType.BLOCK_REMOVED == "block.removed"
        assert EventType.BLOCK_STARTED == "block.started"
        assert EventType.BLOCK_COMPLETED == "block.completed"


class TestEvent:
    """Tests for Event class."""

    def test_basic_event_creation(self):
        """Test creating basic event."""
        event = Event(type=EventType.APP_STARTED)

        assert event.type == EventType.APP_STARTED
        assert isinstance(event.data, dict)
        assert len(event.data) == 0
        assert isinstance(event.timestamp, datetime)
        assert event.source is None

    def test_event_with_data(self):
        """Test creating event with data."""
        data = {"key": "value", "number": 42}
        event = Event(
            type=EventType.WORKFLOW_STARTED,
            data=data
        )

        assert event.data == data
        assert event.data["key"] == "value"
        assert event.data["number"] == 42

    def test_event_with_source(self):
        """Test creating event with source."""
        event = Event(
            type=EventType.PLUGIN_LOADED,
            source="plugin_manager"
        )

        assert event.source == "plugin_manager"

    def test_get_data_value(self):
        """Test getting event data values."""
        event = Event(
            type=EventType.WORKFLOW_STARTED,
            data={"workflow_id": "123", "name": "Test Workflow"}
        )

        assert event.get("workflow_id") == "123"
        assert event.get("name") == "Test Workflow"
        assert event.get("nonexistent") is None
        assert event.get("nonexistent", "default") == "default"

    def test_set_data_value(self):
        """Test setting event data values."""
        event = Event(type=EventType.WORKFLOW_STARTED)

        event.set("workflow_id", "123")
        event.set("status", "running")

        assert event.data["workflow_id"] == "123"
        assert event.data["status"] == "running"

    def test_string_to_event_type_conversion(self):
        """Test conversion of string to EventType."""
        event = Event(type="workflow.started", data={})

        # Should convert string to EventType
        assert event.type == EventType.WORKFLOW_STARTED


class TestEventBus:
    """Tests for EventBus class."""

    def test_initialization(self):
        """Test event bus initialization."""
        bus = EventBus()

        assert isinstance(bus._subscribers, dict)
        assert isinstance(bus._wildcard_subscribers, list)
        assert len(bus._event_history) == 0

    def test_subscribe_to_event(self):
        """Test subscribing to specific event type."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(EventType.WORKFLOW_STARTED, handler)

        event = Event(type=EventType.WORKFLOW_STARTED, data={"test": True})
        bus.publish(event)

        assert len(called) == 1
        assert called[0].type == EventType.WORKFLOW_STARTED

    def test_subscribe_multiple_handlers(self):
        """Test multiple handlers for same event."""
        bus = EventBus()
        calls = {"handler1": 0, "handler2": 0}

        def handler1(event):
            calls["handler1"] += 1

        def handler2(event):
            calls["handler2"] += 1

        bus.subscribe(EventType.WORKFLOW_STARTED, handler1)
        bus.subscribe(EventType.WORKFLOW_STARTED, handler2)

        event = Event(type=EventType.WORKFLOW_STARTED)
        bus.publish(event)

        assert calls["handler1"] == 1
        assert calls["handler2"] == 1

    def test_wildcard_subscription(self):
        """Test subscribing to all events."""
        bus = EventBus()
        called = []

        def wildcard_handler(event):
            called.append(event)

        bus.subscribe_all(wildcard_handler)

        # Publish different event types
        bus.publish(Event(type=EventType.WORKFLOW_STARTED))
        bus.publish(Event(type=EventType.BLOCK_ADDED))
        bus.publish(Event(type=EventType.APP_STARTED))

        assert len(called) == 3

    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(EventType.WORKFLOW_STARTED, handler)

        # Publish event - should be handled
        bus.publish(Event(type=EventType.WORKFLOW_STARTED))
        assert len(called) == 1

        # Unsubscribe
        bus.unsubscribe(EventType.WORKFLOW_STARTED, handler)

        # Publish again - should not be handled
        bus.publish(Event(type=EventType.WORKFLOW_STARTED))
        assert len(called) == 1

    def test_unsubscribe_wildcard(self):
        """Test unsubscribing from wildcard."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe_all(handler)

        # Publish - should be handled
        bus.publish(Event(type=EventType.WORKFLOW_STARTED))
        assert len(called) == 1

        # Unsubscribe
        bus.unsubscribe_all(handler)

        # Publish - should not be handled
        bus.publish(Event(type=EventType.WORKFLOW_STARTED))
        assert len(called) == 1

    def test_emit_convenience_method(self):
        """Test emit convenience method."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(EventType.WORKFLOW_COMPLETED, handler)

        # Use emit method
        bus.emit(
            EventType.WORKFLOW_COMPLETED,
            data={"workflow_id": "123"},
            source="test"
        )

        assert len(called) == 1
        assert called[0].get("workflow_id") == "123"
        assert called[0].source == "test"

    def test_event_history(self):
        """Test event history tracking."""
        bus = EventBus()

        # Publish several events
        bus.emit(EventType.APP_STARTED)
        bus.emit(EventType.WORKFLOW_CREATED)
        bus.emit(EventType.WORKFLOW_STARTED)

        history = bus.get_history()

        assert len(history) == 3
        assert history[0].type == EventType.APP_STARTED
        assert history[1].type == EventType.WORKFLOW_CREATED
        assert history[2].type == EventType.WORKFLOW_STARTED

    def test_event_history_limit(self):
        """Test event history is limited."""
        bus = EventBus()
        bus._max_history = 5  # Set small limit for testing

        # Publish more events than limit
        for i in range(10):
            bus.emit(EventType.APP_STARTED, data={"index": i})

        history = bus.get_history()

        # Should only keep last 5
        assert len(history) == 5
        assert history[0].get("index") == 5
        assert history[-1].get("index") == 9

    def test_get_history_with_count(self):
        """Test getting limited history."""
        bus = EventBus()

        for i in range(10):
            bus.emit(EventType.APP_STARTED, data={"index": i})

        # Get last 3 events
        recent = bus.get_history(count=3)

        assert len(recent) == 3
        assert recent[0].get("index") == 7
        assert recent[-1].get("index") == 9

    def test_clear_history(self):
        """Test clearing event history."""
        bus = EventBus()

        bus.emit(EventType.APP_STARTED)
        bus.emit(EventType.WORKFLOW_STARTED)

        assert len(bus.get_history()) > 0

        bus.clear_history()

        assert len(bus.get_history()) == 0

    def test_clear_subscribers(self):
        """Test clearing all subscribers."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(EventType.WORKFLOW_STARTED, handler)
        bus.subscribe_all(handler)

        bus.clear_subscribers()

        # Publish event - should not be handled
        bus.emit(EventType.WORKFLOW_STARTED)

        assert len(called) == 0

    def test_handler_exception_doesnt_break_other_handlers(self):
        """Test that exception in one handler doesn't affect others."""
        bus = EventBus()
        calls = {"good1": 0, "good2": 0}

        def bad_handler(event):
            raise ValueError("Handler failed")

        def good_handler1(event):
            calls["good1"] += 1

        def good_handler2(event):
            calls["good2"] += 1

        bus.subscribe(EventType.WORKFLOW_STARTED, good_handler1)
        bus.subscribe(EventType.WORKFLOW_STARTED, bad_handler)
        bus.subscribe(EventType.WORKFLOW_STARTED, good_handler2)

        # Should not raise exception
        bus.emit(EventType.WORKFLOW_STARTED)

        # Good handlers should still be called
        assert calls["good1"] == 1
        assert calls["good2"] == 1


class TestGlobalEventBus:
    """Tests for global event bus instance."""

    def test_get_event_bus_singleton(self):
        """Test that get_event_bus returns singleton."""
        bus1 = get_event_bus()
        bus2 = get_event_bus()

        assert bus1 is bus2

    def test_emit_event_function(self):
        """Test emit_event convenience function."""
        bus = get_event_bus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(EventType.PLUGIN_LOADED, handler)

        # Use global emit function
        emit_event(
            EventType.PLUGIN_LOADED,
            data={"plugin": "test"},
            source="test"
        )

        assert len(called) == 1
        assert called[0].get("plugin") == "test"
