"""
Task model for scheduler.

Represents a scheduled task with all configuration and status information.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class TriggerType(Enum):
    """Task trigger types."""
    
    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"
    EVENT = "event"


class TaskStatus(Enum):
    """Task execution status."""
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Task:
    """Scheduled task with execution configuration."""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Workflow to execute
    workflow_id: str = ""
    workflow_path: str = ""
    
    # Schedule
    trigger_type: TriggerType = TriggerType.CRON
    cron_expression: Optional[str] = None  # "0 */6 * * *"
    interval_seconds: Optional[int] = None  # 3600
    run_date: Optional[datetime] = None  # Specific date/time
    event_name: Optional[str] = None  # For event-based triggers
    
    # Execution options
    enabled: bool = True
    max_instances: int = 1  # Max parallel executions
    misfire_grace_time: int = 300  # Seconds
    timeout: Optional[int] = None  # Execution timeout in seconds
    retry_count: int = 0  # Number of retries on failure
    retry_delay: int = 60  # Delay between retries in seconds
    
    # Notifications
    notify_on_success: bool = False
    notify_on_error: bool = True
    notify_on_start: bool = False
    notifications: List[str] = field(default_factory=list)  # ['email', 'telegram']
    
    # Email settings
    email_to: Optional[str] = None
    email_subject: Optional[str] = None
    
    # Telegram settings
    telegram_chat_id: Optional[str] = None
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    
    # Discord settings
    discord_webhook_url: Optional[str] = None
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    last_run: Optional[datetime] = None
    last_result: Optional[Any] = None
    last_error: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'workflow_id': self.workflow_id,
            'workflow_path': self.workflow_path,
            'trigger_type': self.trigger_type.value if isinstance(self.trigger_type, TriggerType) else self.trigger_type,
            'cron_expression': self.cron_expression,
            'interval_seconds': self.interval_seconds,
            'run_date': self.run_date.isoformat() if self.run_date else None,
            'event_name': self.event_name,
            'enabled': self.enabled,
            'max_instances': self.max_instances,
            'misfire_grace_time': self.misfire_grace_time,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'notify_on_success': self.notify_on_success,
            'notify_on_error': self.notify_on_error,
            'notify_on_start': self.notify_on_start,
            'notifications': self.notifications,
            'email_to': self.email_to,
            'telegram_chat_id': self.telegram_chat_id,
            'slack_webhook_url': self.slack_webhook_url,
            'discord_webhook_url': self.discord_webhook_url,
            'status': self.status.value if isinstance(self.status, TaskStatus) else self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_error': self.last_error,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary.
        
        Args:
            data: Dictionary with task data
            
        Returns:
            Task instance
        """
        # Parse enums
        if 'trigger_type' in data and isinstance(data['trigger_type'], str):
            data['trigger_type'] = TriggerType(data['trigger_type'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
        
        # Parse dates
        for date_field in ['last_run', 'run_date', 'created_at', 'updated_at']:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def update_status(self, status: TaskStatus, error: Optional[str] = None) -> None:
        """Update task status.
        
        Args:
            status: New status
            error: Error message if failed
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == TaskStatus.SUCCESS:
            self.success_count += 1
        elif status == TaskStatus.FAILED:
            self.failure_count += 1
            if error:
                self.last_error = error
    
    def record_run(self, success: bool, result: Any = None, error: Optional[str] = None) -> None:
        """Record task execution.
        
        Args:
            success: Whether execution was successful
            result: Execution result
            error: Error message if failed
        """
        self.last_run = datetime.now()
        self.run_count += 1
        
        if success:
            self.status = TaskStatus.SUCCESS
            self.success_count += 1
            self.last_result = result
            self.last_error = None
        else:
            self.status = TaskStatus.FAILED
            self.failure_count += 1
            self.last_error = error
        
        self.updated_at = datetime.now()
