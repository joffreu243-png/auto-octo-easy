"""
Workflow Executor - Engine for executing workflows.

This module handles the execution of workflows by traversing blocks
and executing their actions.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from datetime import datetime
from loguru import logger

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType
from octomaster.automation.browser import Browser


class ExecutionStatus(Enum):
    """Status of workflow execution."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionResult:
    """Result of block execution."""

    def __init__(
        self,
        block_id: str,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
        duration: float = 0.0,
    ):
        self.block_id = block_id
        self.success = success
        self.output = output
        self.error = error
        self.duration = duration
        self.timestamp = datetime.now()

    def __repr__(self) -> str:
        return f"ExecutionResult(block={self.block_id}, success={self.success})"


class WorkflowExecutor:
    """
    Executes workflows by traversing blocks and running their actions.

    Features:
    - Async execution for performance
    - Error handling and retries
    - Variable management
    - Callback system for events
    - Pause/Resume support
    """

    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.status = ExecutionStatus.IDLE
        self.browser: Optional[Browser] = None
        self.variables: Dict[str, Any] = {}
        self.results: List[ExecutionResult] = []
        self.current_block_id: Optional[str] = None

        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "execution_started": [],
            "execution_completed": [],
            "execution_failed": [],
            "block_started": [],
            "block_completed": [],
            "block_failed": [],
        }

        # Control flags
        self._should_stop = False
        self._should_pause = False

        # Stats
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    async def execute(self, headless: bool = False) -> bool:
        """
        Execute the workflow.

        Args:
            headless: Run browser in headless mode

        Returns:
            True if execution was successful, False otherwise
        """
        logger.info(f"Starting execution of workflow: {self.workflow.name}")

        # Validate workflow
        is_valid, errors = self.workflow.validate()
        if not is_valid:
            logger.error(f"Workflow validation failed: {errors}")
            self._trigger_callbacks("execution_failed", errors)
            return False

        # Reset state
        self.status = ExecutionStatus.RUNNING
        self.results = []
        self.variables = {}
        self._should_stop = False
        self._should_pause = False
        self.start_time = datetime.now()

        self._trigger_callbacks("execution_started", self.workflow)

        try:
            # Initialize browser
            self.browser = Browser(headless=headless)
            await self.browser.start()

            # Get entry blocks (blocks with no inputs)
            entry_blocks = self.workflow.get_entry_blocks()
            logger.info(f"Found {len(entry_blocks)} entry blocks")

            # Execute each entry block and its descendants
            for block in entry_blocks:
                if self._should_stop:
                    break

                await self._execute_block_chain(block)

            # Execution completed
            self.status = ExecutionStatus.COMPLETED
            self.end_time = datetime.now()

            logger.info(
                f"Workflow execution completed in {(self.end_time - self.start_time).total_seconds():.2f}s"
            )

            self._trigger_callbacks("execution_completed", self.results)
            return True

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            self.status = ExecutionStatus.FAILED
            self.end_time = datetime.now()

            self._trigger_callbacks("execution_failed", str(e))
            return False

        finally:
            # Cleanup
            if self.browser:
                await self.browser.stop()

    async def _execute_block_chain(self, block: Block):
        """Execute a block and all its connected blocks."""
        if not block.enabled:
            logger.debug(f"Skipping disabled block: {block.name}")
            return

        # Execute the block
        result = await self._execute_block(block)

        # If block failed and retry is not enabled, stop
        if not result.success and not self.workflow.retry_on_error:
            logger.error(f"Block execution failed, stopping workflow")
            self._should_stop = True
            return

        # Get next blocks
        next_blocks = self.workflow.get_next_blocks(block.id)

        # Execute next blocks
        for next_block in next_blocks:
            if self._should_stop:
                break

            await self._execute_block_chain(next_block)

    async def _execute_block(self, block: Block) -> ExecutionResult:
        """Execute a single block."""
        self.current_block_id = block.id
        logger.info(f"Executing block: {block.name} ({block.type.value})")

        self._trigger_callbacks("block_started", block)

        start_time = datetime.now()

        try:
            # Execute based on block type
            output = await self._execute_block_action(block)

            # Success
            duration = (datetime.now() - start_time).total_seconds()
            result = ExecutionResult(
                block_id=block.id, success=True, output=output, duration=duration
            )

            logger.info(f"Block completed successfully in {duration:.2f}s")
            self._trigger_callbacks("block_completed", block, result)

            self.results.append(result)
            return result

        except Exception as e:
            # Failure
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)

            logger.error(f"Block execution failed: {error_msg}")

            result = ExecutionResult(
                block_id=block.id, success=False, error=error_msg, duration=duration
            )

            self._trigger_callbacks("block_failed", block, result)

            self.results.append(result)

            # Retry if enabled
            if self.workflow.retry_on_error:
                for attempt in range(self.workflow.max_retries):
                    logger.info(f"Retrying block (attempt {attempt + 1}/{self.workflow.max_retries})")
                    try:
                        output = await self._execute_block_action(block)
                        result.success = True
                        result.output = output
                        result.error = None
                        logger.info("Retry successful")
                        break
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {retry_error}")
                        result.error = str(retry_error)

            return result

    async def _execute_block_action(self, block: Block) -> Any:
        """Execute the action for a specific block type."""
        if not self.browser:
            raise RuntimeError("Browser not initialized")

        block_type = block.type

        # Navigation blocks
        if block_type == BlockType.OPEN_URL:
            url = block.get_parameter("url", "")
            await self.browser.navigate(url)
            return url

        elif block_type == BlockType.GO_BACK:
            await self.browser.page.go_back()

        elif block_type == BlockType.GO_FORWARD:
            await self.browser.page.go_forward()

        elif block_type == BlockType.REFRESH:
            await self.browser.page.reload()

        # Action blocks
        elif block_type == BlockType.CLICK:
            selector = block.get_parameter("selector", "")
            await self.browser.click(selector)

        elif block_type == BlockType.TYPE_TEXT:
            selector = block.get_parameter("selector", "")
            text = block.get_parameter("text", "")
            # Replace variables in text
            text = self._replace_variables(text)
            await self.browser.type_text(selector, text)

        elif block_type == BlockType.HOVER:
            selector = block.get_parameter("selector", "")
            await self.browser.page.hover(selector)

        elif block_type == BlockType.SCROLL:
            x = block.get_parameter("x", 0)
            y = block.get_parameter("y", 0)
            await self.browser.page.evaluate(f"window.scrollTo({x}, {y})")

        # Wait blocks
        elif block_type == BlockType.WAIT_FOR_ELEMENT:
            selector = block.get_parameter("selector", "")
            timeout = block.get_parameter("timeout", 30000)
            await self.browser.wait_for_selector(selector, timeout=timeout)

        elif block_type == BlockType.WAIT_TIME:
            duration = block.get_parameter("duration", 1000)
            await asyncio.sleep(duration / 1000.0)

        elif block_type == BlockType.WAIT_FOR_LOAD:
            await self.browser.page.wait_for_load_state("networkidle")

        # Data extraction blocks
        elif block_type == BlockType.GET_TEXT:
            selector = block.get_parameter("selector", "")
            text = await self.browser.get_text(selector)
            var_name = block.get_parameter("variable", "text")
            self.variables[var_name] = text
            return text

        elif block_type == BlockType.GET_ATTRIBUTE:
            selector = block.get_parameter("selector", "")
            attribute = block.get_parameter("attribute", "href")
            element = await self.browser.page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                var_name = block.get_parameter("variable", "attribute")
                self.variables[var_name] = value
                return value

        elif block_type == BlockType.SCREENSHOT:
            path = block.get_parameter("path", "screenshot.png")
            await self.browser.screenshot(path)
            return path

        elif block_type == BlockType.GET_COOKIES:
            cookies = await self.browser.context.cookies()
            self.variables["cookies"] = cookies
            return cookies

        # Variable blocks
        elif block_type == BlockType.VARIABLE:
            var_name = block.get_parameter("name", "var")
            var_value = block.get_parameter("value", "")
            self.variables[var_name] = var_value
            return var_value

        else:
            logger.warning(f"Block type not implemented: {block_type.value}")

        return None

    def _replace_variables(self, text: str) -> str:
        """Replace variables in text like {{variable_name}}."""
        import re

        def replace(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, match.group(0)))

        return re.sub(r"\{\{(\w+)\}\}", replace, text)

    def pause(self):
        """Pause execution."""
        self._should_pause = True
        self.status = ExecutionStatus.PAUSED
        logger.info("Execution paused")

    def resume(self):
        """Resume execution."""
        self._should_pause = False
        self.status = ExecutionStatus.RUNNING
        logger.info("Execution resumed")

    def stop(self):
        """Stop execution."""
        self._should_stop = True
        self.status = ExecutionStatus.CANCELLED
        logger.info("Execution stopped")

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

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.start_time:
            return {}

        duration = 0.0
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful

        return {
            "status": self.status.value,
            "duration": duration,
            "total_blocks": len(self.results),
            "successful": successful,
            "failed": failed,
            "variables": dict(self.variables),
        }

    def __repr__(self) -> str:
        return f"WorkflowExecutor(workflow={self.workflow.name}, status={self.status.value})"
