"""
Task executor for running scheduled workflows.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import asyncio

from src.scheduler.task import Task, TaskStatus


class TaskExecutor:
    """Execute scheduled tasks."""
    
    def __init__(self, task: Task) -> None:
        """Initialize executor.
        
        Args:
            task: Task to execute
        """
        self.task = task
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the task.
        
        Returns:
            Execution result dictionary
        """
        self.start_time = datetime.now()
        logger.info(f"Executing task: {self.task.name}")
        
        try:
            # Load workflow
            workflow = await self._load_workflow()
            
            if not workflow:
                raise Exception("Failed to load workflow")
            
            # Execute workflow with timeout if specified
            if self.task.timeout:
                result = await asyncio.wait_for(
                    self._execute_workflow(workflow),
                    timeout=self.task.timeout
                )
            else:
                result = await self._execute_workflow(workflow)
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"Task '{self.task.name}' completed in {duration:.2f}s")
            
            return {
                'success': True,
                'result': result,
                'duration': duration,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
            }
        
        except asyncio.TimeoutError:
            self.end_time = datetime.now()
            error_msg = f"Task timed out after {self.task.timeout}s"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'duration': (self.end_time - self.start_time).total_seconds(),
            }
        
        except Exception as e:
            self.end_time = datetime.now()
            error_msg = str(e)
            logger.error(f"Task execution failed: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': (self.end_time - self.start_time).total_seconds() if self.start_time else 0,
            }
    
    async def _load_workflow(self) -> Optional[Any]:
        """Load workflow from file.
        
        Returns:
            Workflow object or None
        """
        try:
            from src.nodes.serializer import WorkflowSerializer
            
            serializer = WorkflowSerializer()
            workflow_path = Path(self.task.workflow_path)
            
            if not workflow_path.exists():
                logger.error(f"Workflow file not found: {workflow_path}")
                return None
            
            blocks, connections_data = serializer.load_from_file(workflow_path)
            
            logger.debug(f"Loaded workflow: {len(blocks)} blocks")
            
            return {
                'blocks': blocks,
                'connections': connections_data,
            }
        
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return None
    
    async def _execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow.
        
        Args:
            workflow: Workflow data
            
        Returns:
            Execution result
        """
        try:
            from src.nodes.executor import WorkflowExecutor
            
            # Get browser if needed (placeholder)
            browser = None  # TODO: Initialize browser from config
            
            # Create executor
            executor = WorkflowExecutor(
                workflow['blocks'],
                []  # connections - TODO: recreate from connections_data
            )
            
            # Execute
            result = await executor.execute(browser)
            
            return {
                'status': result.status.value if hasattr(result, 'status') else 'unknown',
                'executed_blocks': result.executed_blocks if hasattr(result, 'executed_blocks') else 0,
                'errors': result.errors if hasattr(result, 'errors') else [],
            }
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise
    
    async def execute_with_retry(self) -> Dict[str, Any]:
        """Execute with retry logic.
        
        Returns:
            Execution result
        """
        last_error = None
        
        for attempt in range(self.task.retry_count + 1):
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{self.task.retry_count}")
                await asyncio.sleep(self.task.retry_delay)
            
            result = await self.execute()
            
            if result['success']:
                return result
            
            last_error = result.get('error')
        
        # All retries failed
        return {
            'success': False,
            'error': f"Failed after {self.task.retry_count + 1} attempts. Last error: {last_error}",
            'retries': self.task.retry_count,
        }
