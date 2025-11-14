"""
Main task scheduler for OctoMaster Pro.

Manages scheduled tasks and executes them using APScheduler.
"""

from typing import Dict, Optional, List
from datetime import datetime
import asyncio
from loguru import logger

from src.scheduler.task import Task, TaskStatus, TriggerType
from src.scheduler.storage import TaskStorage
from src.scheduler.executor import TaskExecutor


class TaskScheduler:
    """Main task scheduler with APScheduler integration."""
    
    def __init__(self, storage_path: Optional[str] = None) -> None:
        """Initialize scheduler.
        
        Args:
            storage_path: Path to task storage file
        """
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        
        self.scheduler = AsyncIOScheduler()
        self.storage = TaskStorage(storage_path)
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Notification system
        self.notifiers = {}
        
        logger.info("Task scheduler initialized")
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
            
            # Load tasks from storage
            self._load_tasks_from_storage()
    
    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            # Cancel running tasks
            for task_id, task_future in self.running_tasks.items():
                if not task_future.done():
                    task_future.cancel()
            
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def add_task(self, task: Task) -> bool:
        """Add task to scheduler.
        
        Args:
            task: Task object
            
        Returns:
            True if added successfully
        """
        try:
            self.tasks[task.id] = task
            
            # Create trigger
            trigger = self._create_trigger(task)
            
            if not trigger:
                logger.error(f"Failed to create trigger for task: {task.name}")
                return False
            
            # Add job to APScheduler
            self.scheduler.add_job(
                func=self._execute_task_wrapper,
                trigger=trigger,
                args=[task.id],
                id=task.id,
                name=task.name,
                misfire_grace_time=task.misfire_grace_time,
                max_instances=task.max_instances,
            )
            
            # Save to storage
            self.storage.save_task(task)
            
            logger.info(f"Task '{task.name}' scheduled ({task.trigger_type.value})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return False
    
    def _create_trigger(self, task: Task):
        """Create APScheduler trigger from task.
        
        Args:
            task: Task object
            
        Returns:
            APScheduler trigger or None
        """
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger
        from apscheduler.triggers.date import DateTrigger
        
        if task.trigger_type == TriggerType.CRON:
            if not task.cron_expression:
                return None
            return CronTrigger.from_crontab(task.cron_expression)
        
        elif task.trigger_type == TriggerType.INTERVAL:
            if not task.interval_seconds:
                return None
            return IntervalTrigger(seconds=task.interval_seconds)
        
        elif task.trigger_type == TriggerType.DATE:
            if not task.run_date:
                return None
            return DateTrigger(run_date=task.run_date)
        
        return None
    
    async def _execute_task_wrapper(self, task_id: str) -> None:
        """Wrapper for async task execution.
        
        Args:
            task_id: Task ID
        """
        # Create async task
        task_future = asyncio.create_task(self._execute_task(task_id))
        self.running_tasks[task_id] = task_future
        
        try:
            await task_future
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def _execute_task(self, task_id: str) -> None:
        """Execute scheduled task.
        
        Args:
            task_id: Task ID
        """
        task = self.tasks.get(task_id)
        
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        if not task.enabled:
            logger.info(f"Task '{task.name}' is disabled, skipping")
            return
        
        logger.info(f"Executing task: {task.name}")
        
        # Update status
        task.update_status(TaskStatus.RUNNING)
        
        # Send start notification
        if task.notify_on_start:
            await self._send_notification(task, 'running', 'Task execution started')
        
        try:
            # Create executor
            executor = TaskExecutor(task)
            
            # Execute with retry if configured
            if task.retry_count > 0:
                result = await executor.execute_with_retry()
            else:
                result = await executor.execute()
            
            # Update task status
            if result['success']:
                task.record_run(True, result)
                
                # Send success notification
                if task.notify_on_success:
                    message = f"Task completed successfully\nDuration: {result.get('duration', 0):.2f}s"
                    await self._send_notification(task, 'success', message)
                
                logger.info(f"Task '{task.name}' completed successfully")
            
            else:
                error = result.get('error', 'Unknown error')
                task.record_run(False, error=error)
                
                # Send error notification
                if task.notify_on_error:
                    message = f"Task failed\nError: {error}"
                    await self._send_notification(task, 'failed', message)
                
                logger.error(f"Task '{task.name}' failed: {error}")
            
            # Save updated task
            self.storage.save_task(task)
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Task '{task.name}' execution error: {error_msg}")
            
            task.record_run(False, error=error_msg)
            
            # Send error notification
            if task.notify_on_error:
                await self._send_notification(task, 'failed', f"Execution error: {error_msg}")
            
            # Save updated task
            self.storage.save_task(task)
    
    async def _send_notification(self, task: Task, status: str, message: str) -> None:
        """Send notifications about task execution.
        
        Args:
            task: Task object
            status: Task status
            message: Notification message
        """
        for notification_type in task.notifications:
            try:
                if notification_type == 'email' and 'email' in self.notifiers:
                    await self.notifiers['email'].send_task_notification(task, status, message)
                
                elif notification_type == 'telegram' and 'telegram' in self.notifiers:
                    await self.notifiers['telegram'].send_task_notification(task, status, message)
                
                elif notification_type == 'desktop' and 'desktop' in self.notifiers:
                    await self.notifiers['desktop'].send_task_notification(task, status, message)
            
            except Exception as e:
                logger.error(f"Failed to send {notification_type} notification: {e}")
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from scheduler.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if removed
        """
        try:
            if task_id in self.tasks:
                self.scheduler.remove_job(task_id)
                del self.tasks[task_id]
                self.storage.delete_task(task_id)
                logger.info(f"Task {task_id} removed")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Failed to remove task: {e}")
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """Pause task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if paused
        """
        try:
            self.scheduler.pause_job(task_id)
            
            if task_id in self.tasks:
                self.tasks[task_id].update_status(TaskStatus.PAUSED)
                self.storage.save_task(self.tasks[task_id])
            
            logger.info(f"Task {task_id} paused")
            return True
        
        except Exception as e:
            logger.error(f"Failed to pause task: {e}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if resumed
        """
        try:
            self.scheduler.resume_job(task_id)
            
            if task_id in self.tasks:
                self.tasks[task_id].update_status(TaskStatus.PENDING)
                self.storage.save_task(self.tasks[task_id])
            
            logger.info(f"Task {task_id} resumed")
            return True
        
        except Exception as e:
            logger.error(f"Failed to resume task: {e}")
            return False
    
    def get_tasks(self) -> List[Task]:
        """Get all scheduled tasks.
        
        Returns:
            List of tasks
        """
        return list(self.tasks.values())
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None
        """
        return self.tasks.get(task_id)
    
    def _load_tasks_from_storage(self) -> None:
        """Load tasks from storage and schedule them."""
        tasks = self.storage.get_enabled_tasks()
        
        for task in tasks:
            try:
                self.add_task(task)
            except Exception as e:
                logger.error(f"Failed to load task {task.name}: {e}")
        
        logger.info(f"Loaded {len(tasks)} tasks from storage")
    
    def configure_notifications(self, email_config: Optional[Dict] = None,
                               telegram_config: Optional[Dict] = None) -> None:
        """Configure notification systems.
        
        Args:
            email_config: Email configuration
            telegram_config: Telegram configuration
        """
        if email_config:
            from src.scheduler.notifications.email import EmailNotifier
            self.notifiers['email'] = EmailNotifier(**email_config)
        
        if telegram_config:
            from src.scheduler.notifications.telegram import TelegramNotifier
            self.notifiers['telegram'] = TelegramNotifier(**telegram_config)
        
        # Desktop notifications (no config needed)
        from src.scheduler.notifications.desktop import DesktopNotifier
        self.notifiers['desktop'] = DesktopNotifier()
