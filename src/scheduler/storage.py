"""
Task storage for persistence.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from loguru import logger

from src.scheduler.task import Task


class TaskStorage:
    """Store and load scheduled tasks."""
    
    def __init__(self, storage_path: Path = None) -> None:
        """Initialize task storage.
        
        Args:
            storage_path: Path to storage file
        """
        self.storage_path = storage_path or Path("data/tasks.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_task(self, task: Task) -> bool:
        """Save single task.
        
        Args:
            task: Task to save
            
        Returns:
            True if successful
        """
        try:
            tasks = self.load_all_tasks()
            
            # Update or add task
            existing_index = next((i for i, t in enumerate(tasks) if t.id == task.id), None)
            
            if existing_index is not None:
                tasks[existing_index] = task
            else:
                tasks.append(task)
            
            return self.save_all_tasks(tasks)
        
        except Exception as e:
            logger.error(f"Failed to save task: {e}")
            return False
    
    def save_all_tasks(self, tasks: List[Task]) -> bool:
        """Save all tasks.
        
        Args:
            tasks: List of tasks
            
        Returns:
            True if successful
        """
        try:
            data = {
                'tasks': [task.to_dict() for task in tasks],
                'version': '1.0',
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(tasks)} tasks")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
            return False
    
    def load_task(self, task_id: str) -> Optional[Task]:
        """Load single task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None
        """
        tasks = self.load_all_tasks()
        return next((t for t in tasks if t.id == task_id), None)
    
    def load_all_tasks(self) -> List[Task]:
        """Load all tasks.
        
        Returns:
            List of tasks
        """
        try:
            if not self.storage_path.exists():
                return []
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = [Task.from_dict(task_data) for task_data in data.get('tasks', [])]
            
            logger.debug(f"Loaded {len(tasks)} tasks")
            return tasks
        
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            return []
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful
        """
        try:
            tasks = self.load_all_tasks()
            tasks = [t for t in tasks if t.id != task_id]
            return self.save_all_tasks(tasks)
        
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False
    
    def get_enabled_tasks(self) -> List[Task]:
        """Get all enabled tasks.
        
        Returns:
            List of enabled tasks
        """
        tasks = self.load_all_tasks()
        return [t for t in tasks if t.enabled]
    
    def clear(self) -> bool:
        """Clear all tasks.
        
        Returns:
            True if successful
        """
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to clear tasks: {e}")
            return False
