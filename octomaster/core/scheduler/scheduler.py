"""
Task Scheduler for workflow automation.

Supports:
- One-time execution
- Recurring schedules (interval, cron)
- Event-based triggers
- Calendar visualization
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
from loguru import logger

from octomaster.core.workflow import Workflow
from octomaster.automation.executor import WorkflowExecutor


class ScheduleType(Enum):
    """Type of schedule."""

    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    EVENT = "event"


@dataclass
class ScheduledTask:
    """A scheduled workflow task."""

    id: str
    name: str
    workflow_path: Path
    schedule_type: ScheduleType
    enabled: bool = True

    # Schedule parameters
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Interval parameters
    interval_seconds: Optional[int] = None
    interval_minutes: Optional[int] = None
    interval_hours: Optional[int] = None
    interval_days: Optional[int] = None

    # Cron parameters
    cron_expression: Optional[str] = None

    # Execution settings
    max_retries: int = 3
    timeout: int = 3600  # seconds
    headless: bool = True

    # Notifications
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    # Tags
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "workflow_path": str(self.workflow_path),
            "schedule_type": self.schedule_type.value,
            "enabled": self.enabled,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "interval_seconds": self.interval_seconds,
            "interval_minutes": self.interval_minutes,
            "interval_hours": self.interval_hours,
            "interval_days": self.interval_days,
            "cron_expression": self.cron_expression,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "headless": self.headless,
            "notify_on_success": self.notify_on_success,
            "notify_on_failure": self.notify_on_failure,
            "notification_channels": self.notification_channels,
            "tags": self.tags,
            "stats": {
                "run_count": self.run_count,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "last_run": self.last_run.isoformat() if self.last_run else None,
                "next_run": self.next_run.isoformat() if self.next_run else None,
            },
        }


class TaskScheduler:
    """
    Manages scheduled workflow executions.

    Features:
    - Multiple schedule types (once, interval, cron)
    - Calendar visualization
    - Execution history
    - Notifications
    - Pause/Resume
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, ScheduledTask] = {}
        self.jobs: Dict[str, Job] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            "task_added": [],
            "task_removed": [],
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
        }

        logger.info("Task Scheduler initialized")

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler stopped")

    def add_task(self, task: ScheduledTask) -> bool:
        """
        Add a scheduled task.

        Args:
            task: ScheduledTask to add

        Returns:
            True if successful
        """
        try:
            # Determine trigger based on schedule type
            trigger = self._create_trigger(task)

            if not trigger:
                logger.error(f"Failed to create trigger for task {task.name}")
                return False

            # Add job to scheduler
            job = self.scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=task.id,
                name=task.name,
                args=[task],
                max_instances=1,
                replace_existing=True,
            )

            # Store task and job
            self.tasks[task.id] = task
            self.jobs[task.id] = job

            # Update next run time
            if job.next_run_time:
                task.next_run = job.next_run_time

            logger.info(f"Added scheduled task: {task.name} (next run: {task.next_run})")

            self._trigger_callbacks("task_added", task)
            return True

        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return False

    def _create_trigger(self, task: ScheduledTask):
        """Create APScheduler trigger from task."""
        if task.schedule_type == ScheduleType.ONCE:
            # One-time execution
            return DateTrigger(run_date=task.start_date or datetime.now())

        elif task.schedule_type == ScheduleType.INTERVAL:
            # Recurring interval
            return IntervalTrigger(
                seconds=task.interval_seconds or 0,
                minutes=task.interval_minutes or 0,
                hours=task.interval_hours or 0,
                days=task.interval_days or 0,
                start_date=task.start_date,
                end_date=task.end_date,
            )

        elif task.schedule_type == ScheduleType.CRON:
            # Cron expression
            if not task.cron_expression:
                return None
            return CronTrigger.from_crontab(task.cron_expression)

        return None

    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task."""
        logger.info(f"Executing scheduled task: {task.name}")

        task.last_run = datetime.now()
        task.run_count += 1

        self._trigger_callbacks("task_started", task)

        try:
            # Load workflow
            workflow = Workflow.load(task.workflow_path)

            # Execute workflow
            executor = WorkflowExecutor(workflow)
            success = await executor.execute(headless=task.headless)

            # Update stats
            if success:
                task.success_count += 1
                logger.info(f"Task completed successfully: {task.name}")

                if task.notify_on_success:
                    await self._send_notification(
                        task, "success", f"Task '{task.name}' completed successfully"
                    )

                self._trigger_callbacks("task_completed", task, executor)
            else:
                task.failure_count += 1
                logger.error(f"Task failed: {task.name}")

                if task.notify_on_failure:
                    await self._send_notification(
                        task, "failure", f"Task '{task.name}' failed"
                    )

                self._trigger_callbacks("task_failed", task, executor)

        except Exception as e:
            task.failure_count += 1
            logger.error(f"Task execution error: {e}", exc_info=True)

            if task.notify_on_failure:
                await self._send_notification(task, "error", f"Task '{task.name}' error: {e}")

            self._trigger_callbacks("task_failed", task, str(e))

        # Update next run time
        job = self.jobs.get(task.id)
        if job and job.next_run_time:
            task.next_run = job.next_run_time

    async def _send_notification(self, task: ScheduledTask, status: str, message: str):
        """Send notification for task execution."""
        # TODO: Implement notification sending
        logger.info(f"Notification: {message}")

    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task."""
        if task_id not in self.tasks:
            return False

        try:
            # Remove job from scheduler
            self.scheduler.remove_job(task_id)

            # Remove from storage
            task = self.tasks.pop(task_id)
            self.jobs.pop(task_id, None)

            logger.info(f"Removed task: {task.name}")

            self._trigger_callbacks("task_removed", task)
            return True

        except Exception as e:
            logger.error(f"Failed to remove task: {e}")
            return False

    def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task."""
        if task_id not in self.tasks:
            return False

        try:
            self.scheduler.pause_job(task_id)
            self.tasks[task_id].enabled = False
            logger.info(f"Paused task: {self.tasks[task_id].name}")
            return True

        except Exception as e:
            logger.error(f"Failed to pause task: {e}")
            return False

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        if task_id not in self.tasks:
            return False

        try:
            self.scheduler.resume_job(task_id)
            self.tasks[task_id].enabled = True
            logger.info(f"Resumed task: {self.tasks[task_id].name}")
            return True

        except Exception as e:
            logger.error(f"Failed to resume task: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks."""
        return list(self.tasks.values())

    def get_tasks_by_tag(self, tag: str) -> List[ScheduledTask]:
        """Get tasks with specific tag."""
        return [task for task in self.tasks.values() if tag in task.tags]

    def get_upcoming(self, limit: int = 10) -> List[ScheduledTask]:
        """Get upcoming tasks sorted by next run time."""
        tasks_with_next_run = [t for t in self.tasks.values() if t.next_run]
        sorted_tasks = sorted(tasks_with_next_run, key=lambda t: t.next_run)
        return sorted_tasks[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        total_runs = sum(t.run_count for t in self.tasks.values())
        total_success = sum(t.success_count for t in self.tasks.values())
        total_failures = sum(t.failure_count for t in self.tasks.values())

        return {
            "total_tasks": len(self.tasks),
            "enabled_tasks": sum(1 for t in self.tasks.values() if t.enabled),
            "disabled_tasks": sum(1 for t in self.tasks.values() if not t.enabled),
            "total_runs": total_runs,
            "total_success": total_success,
            "total_failures": total_failures,
            "success_rate": (total_success / total_runs * 100) if total_runs > 0 else 0,
        }

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
                    logger.error(f"Callback error for {event}: {e}")

    def __repr__(self) -> str:
        return f"TaskScheduler(tasks={len(self.tasks)}, running={self.scheduler.running})"
