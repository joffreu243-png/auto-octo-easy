"""
Unit tests for state management.

Tests the AppState class and state management functionality.
"""

import pytest
from datetime import datetime
from pathlib import Path
from src.core.state import (
    AppState,
    AppStatus,
    WorkflowStatus,
    WorkflowState,
    BrowserState,
    RecorderState,
    ExecutionStats,
    get_app_state,
    reset_app_state,
)


class TestAppStatus:
    """Tests for AppStatus enum."""

    def test_app_status_values(self):
        """Test app status enum values."""
        assert AppStatus.IDLE == "idle"
        assert AppStatus.RUNNING == "running"
        assert AppStatus.PAUSED == "paused"
        assert AppStatus.ERROR == "error"


class TestWorkflowStatus:
    """Tests for WorkflowStatus enum."""

    def test_workflow_status_values(self):
        """Test workflow status enum values."""
        assert WorkflowStatus.IDLE == "idle"
        assert WorkflowStatus.RUNNING == "running"
        assert WorkflowStatus.PAUSED == "paused"
        assert WorkflowStatus.COMPLETED == "completed"
        assert WorkflowStatus.FAILED == "failed"
        assert WorkflowStatus.STOPPED == "stopped"


class TestExecutionStats:
    """Tests for ExecutionStats class."""

    def test_default_initialization(self):
        """Test default stats initialization."""
        stats = ExecutionStats()

        assert stats.total_runs == 0
        assert stats.successful_runs == 0
        assert stats.failed_runs == 0
        assert stats.total_blocks_executed == 0
        assert stats.total_execution_time_ms == 0.0
        assert stats.last_execution_time is None

    def test_record_successful_run(self):
        """Test recording successful run."""
        stats = ExecutionStats()

        stats.record_run(success=True, duration_ms=1000.0, blocks_executed=5)

        assert stats.total_runs == 1
        assert stats.successful_runs == 1
        assert stats.failed_runs == 0
        assert stats.total_blocks_executed == 5
        assert stats.total_execution_time_ms == 1000.0
        assert stats.last_execution_time is not None

    def test_record_failed_run(self):
        """Test recording failed run."""
        stats = ExecutionStats()

        stats.record_run(success=False, duration_ms=500.0, blocks_executed=3)

        assert stats.total_runs == 1
        assert stats.successful_runs == 0
        assert stats.failed_runs == 1
        assert stats.total_blocks_executed == 3

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = ExecutionStats()

        # No runs yet
        assert stats.success_rate == 0.0

        # 3 successful, 1 failed = 75%
        stats.record_run(success=True, duration_ms=100)
        stats.record_run(success=True, duration_ms=100)
        stats.record_run(success=True, duration_ms=100)
        stats.record_run(success=False, duration_ms=100)

        assert stats.success_rate == 75.0

    def test_average_execution_time(self):
        """Test average execution time calculation."""
        stats = ExecutionStats()

        # No runs yet
        assert stats.average_execution_time_ms == 0.0

        # 3 runs: 1000ms, 2000ms, 3000ms = avg 2000ms
        stats.record_run(success=True, duration_ms=1000)
        stats.record_run(success=True, duration_ms=2000)
        stats.record_run(success=True, duration_ms=3000)

        assert stats.average_execution_time_ms == 2000.0


class TestWorkflowState:
    """Tests for WorkflowState class."""

    def test_default_initialization(self):
        """Test default workflow state."""
        state = WorkflowState()

        assert state.file_path is None
        assert state.is_modified is False
        assert state.is_executing is False
        assert state.status == WorkflowStatus.IDLE
        assert state.current_block_id is None
        assert len(state.variables) == 0
        assert isinstance(state.stats, ExecutionStats)

    def test_reset_state(self):
        """Test resetting workflow state."""
        state = WorkflowState()

        # Modify state
        state.is_executing = True
        state.status = WorkflowStatus.RUNNING
        state.current_block_id = "block_123"

        # Reset
        state.reset()

        assert state.is_executing is False
        assert state.status == WorkflowStatus.IDLE
        assert state.current_block_id is None

    def test_variables_storage(self):
        """Test storing workflow variables."""
        state = WorkflowState()

        state.variables["name"] = "John"
        state.variables["age"] = 30
        state.variables["active"] = True

        assert state.variables["name"] == "John"
        assert state.variables["age"] == 30
        assert state.variables["active"] is True


class TestBrowserState:
    """Tests for BrowserState class."""

    def test_default_initialization(self):
        """Test default browser state."""
        state = BrowserState()

        assert state.is_active is False
        assert state.current_url is None
        assert state.page_title is None
        assert state.browser_type == "chromium"
        assert state.headless is False

    def test_custom_initialization(self):
        """Test custom browser state."""
        state = BrowserState(
            is_active=True,
            current_url="https://example.com",
            browser_type="firefox",
            headless=True
        )

        assert state.is_active is True
        assert state.current_url == "https://example.com"
        assert state.browser_type == "firefox"
        assert state.headless is True


class TestRecorderState:
    """Tests for RecorderState class."""

    def test_default_initialization(self):
        """Test default recorder state."""
        state = RecorderState()

        assert state.is_recording is False
        assert state.actions_recorded == 0
        assert state.start_time is None

    def test_start_recording(self):
        """Test starting recording."""
        state = RecorderState()

        state.start_recording()

        assert state.is_recording is True
        assert state.actions_recorded == 0
        assert state.start_time is not None
        assert isinstance(state.start_time, datetime)

    def test_stop_recording(self):
        """Test stopping recording."""
        state = RecorderState()

        state.start_recording()
        assert state.is_recording is True

        state.stop_recording()
        assert state.is_recording is False

    def test_record_action(self):
        """Test recording actions."""
        state = RecorderState()

        state.start_recording()

        state.record_action()
        assert state.actions_recorded == 1

        state.record_action()
        state.record_action()
        assert state.actions_recorded == 3


class TestAppState:
    """Tests for AppState class."""

    def test_initialization(self):
        """Test app state initialization."""
        state = AppState()

        assert state.status == AppStatus.IDLE
        assert isinstance(state.start_time, datetime)
        assert isinstance(state.workflow, WorkflowState)
        assert isinstance(state.browser, BrowserState)
        assert isinstance(state.recorder, RecorderState)

    def test_set_and_get_custom_data(self):
        """Test setting and getting custom state data."""
        state = AppState()

        state.set("custom_key", "custom_value")
        state.set("number", 42)
        state.set("boolean", True)

        assert state.get("custom_key") == "custom_value"
        assert state.get("number") == 42
        assert state.get("boolean") is True

    def test_get_with_default(self):
        """Test getting state data with default value."""
        state = AppState()

        assert state.get("nonexistent") is None
        assert state.get("nonexistent", "default") == "default"

    def test_delete_state_data(self):
        """Test deleting state data."""
        state = AppState()

        state.set("key", "value")
        assert state.get("key") == "value"

        state.delete("key")
        assert state.get("key") is None

    def test_clear_state(self):
        """Test clearing all state."""
        state = AppState()

        # Add custom data
        state.set("key1", "value1")
        state.set("key2", "value2")

        # Modify workflow state
        state.workflow.is_executing = True
        state.workflow.status = WorkflowStatus.RUNNING

        # Clear
        state.clear()

        # Custom data should be cleared
        assert state.get("key1") is None
        assert state.get("key2") is None

        # Workflow should be reset
        assert state.workflow.is_executing is False
        assert state.workflow.status == WorkflowStatus.IDLE

    def test_to_dict(self):
        """Test converting state to dictionary."""
        state = AppState()

        state.workflow.file_path = Path("/test/workflow.json")
        state.workflow.is_executing = True
        state.browser.is_active = True
        state.browser.current_url = "https://example.com"

        state_dict = state.to_dict()

        assert isinstance(state_dict, dict)
        assert state_dict["status"] == "idle"
        assert "workflow" in state_dict
        assert "browser" in state_dict
        assert "recorder" in state_dict

        # Check workflow data
        assert state_dict["workflow"]["is_executing"] is True
        assert state_dict["workflow"]["file_path"] == "/test/workflow.json"

        # Check browser data
        assert state_dict["browser"]["is_active"] is True
        assert state_dict["browser"]["current_url"] == "https://example.com"

    def test_uptime_seconds(self):
        """Test uptime calculation."""
        state = AppState()

        # Should be very small (just created)
        assert state.uptime_seconds >= 0
        assert state.uptime_seconds < 1  # Less than 1 second

    def test_workflow_stats_in_dict(self):
        """Test that workflow stats are included in dict."""
        state = AppState()

        # Record some runs
        state.workflow.stats.record_run(success=True, duration_ms=1000)
        state.workflow.stats.record_run(success=False, duration_ms=500)

        state_dict = state.to_dict()

        stats = state_dict["workflow"]["stats"]
        assert stats["total_runs"] == 2
        assert stats["successful_runs"] == 1
        assert stats["failed_runs"] == 1
        assert stats["success_rate"] == 50.0


class TestGlobalAppState:
    """Tests for global app state instance."""

    def test_get_app_state_singleton(self):
        """Test that get_app_state returns singleton."""
        state1 = get_app_state()
        state2 = get_app_state()

        assert state1 is state2

    def test_reset_app_state(self):
        """Test resetting global app state."""
        state = get_app_state()

        # Modify state
        state.set("test_key", "test_value")
        assert state.get("test_key") == "test_value"

        # Reset
        reset_app_state()

        # Get new instance
        new_state = get_app_state()

        # Should be fresh instance
        assert new_state.get("test_key") is None
