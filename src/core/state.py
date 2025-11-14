"""
Application state management for OctoMaster Pro.

This module provides centralized state management for the application,
tracking current workflow, execution status, and runtime state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from pathlib import Path
from enum import Enum
from loguru import logger


class AppStatus(str, Enum):
    """Application status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class ExecutionStats:
    """Execution statistics."""

    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_blocks_executed: int = 0
    total_execution_time_ms: float = 0.0
    last_execution_time: Optional[datetime] = None

    def record_run(self, success: bool, duration_ms: float, blocks_executed: int = 0) -> None:
        """
        Record a workflow run.

        Args:
            success: Whether the run was successful
            duration_ms: Duration in milliseconds
            blocks_executed: Number of blocks executed
        """
        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        self.total_blocks_executed += blocks_executed
        self.total_execution_time_ms += duration_ms
        self.last_execution_time = datetime.now()

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100

    @property
    def average_execution_time_ms(self) -> float:
        """Get average execution time."""
        if self.total_runs == 0:
            return 0.0
        return self.total_execution_time_ms / self.total_runs


@dataclass
class WorkflowState:
    """Current workflow state."""

    file_path: Optional[Path] = None
    is_modified: bool = False
    is_executing: bool = False
    status: WorkflowStatus = WorkflowStatus.IDLE
    current_block_id: Optional[str] = None
    variables: dict[str, Any] = field(default_factory=dict)
    stats: ExecutionStats = field(default_factory=ExecutionStats)

    def reset(self) -> None:
        """Reset workflow state."""
        self.is_executing = False
        self.status = WorkflowStatus.IDLE
        self.current_block_id = None


@dataclass
class BrowserState:
    """Browser state."""

    is_active: bool = False
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    browser_type: str = "chromium"
    headless: bool = False


@dataclass
class RecorderState:
    """Recorder state."""

    is_recording: bool = False
    actions_recorded: int = 0
    start_time: Optional[datetime] = None

    def start_recording(self) -> None:
        """Start recording."""
        self.is_recording = True
        self.actions_recorded = 0
        self.start_time = datetime.now()

    def stop_recording(self) -> None:
        """Stop recording."""
        self.is_recording = False

    def record_action(self) -> None:
        """Record an action."""
        self.actions_recorded += 1


class AppState:
    """
    Central application state manager.

    Maintains the current state of the application including workflow state,
    browser state, recorder state, and execution statistics.
    """

    def __init__(self) -> None:
        """Initialize application state."""
        self.status = AppStatus.IDLE
        self.start_time = datetime.now()
        self.workflow = WorkflowState()
        self.browser = BrowserState()
        self.recorder = RecorderState()
        self._state_data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Set state value.

        Args:
            key: State key
            value: State value
        """
        self._state_data[key] = value
        logger.debug(f"State updated: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state value.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self._state_data.get(key, default)

    def delete(self, key: str) -> None:
        """
        Delete state value.

        Args:
            key: State key to delete
        """
        if key in self._state_data:
            del self._state_data[key]
            logger.debug(f"State deleted: {key}")

    def clear(self) -> None:
        """Clear all state data."""
        self._state_data.clear()
        self.workflow.reset()
        logger.info("Application state cleared")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert state to dictionary.

        Returns:
            State as dictionary
        """
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "workflow": {
                "file_path": str(self.workflow.file_path) if self.workflow.file_path else None,
                "is_modified": self.workflow.is_modified,
                "is_executing": self.workflow.is_executing,
                "status": self.workflow.status.value,
                "current_block_id": self.workflow.current_block_id,
                "variables_count": len(self.workflow.variables),
                "stats": {
                    "total_runs": self.workflow.stats.total_runs,
                    "successful_runs": self.workflow.stats.successful_runs,
                    "failed_runs": self.workflow.stats.failed_runs,
                    "success_rate": self.workflow.stats.success_rate,
                    "average_execution_time_ms": self.workflow.stats.average_execution_time_ms,
                },
            },
            "browser": {
                "is_active": self.browser.is_active,
                "current_url": self.browser.current_url,
                "page_title": self.browser.page_title,
                "browser_type": self.browser.browser_type,
            },
            "recorder": {
                "is_recording": self.recorder.is_recording,
                "actions_recorded": self.recorder.actions_recorded,
            },
            "custom_data": self._state_data,
        }

    @property
    def uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


# Global state instance
_app_state: Optional[AppState] = None


def get_app_state() -> AppState:
    """
    Get global application state instance.

    Returns:
        AppState instance
    """
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


def reset_app_state() -> None:
    """Reset global application state."""
    global _app_state
    _app_state = AppState()
    logger.info("Application state reset")
