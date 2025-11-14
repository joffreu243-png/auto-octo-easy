"""
Workflow execution engine for node-based workflows.

Handles execution of workflow blocks with proper control flow,
loops, conditionals, and error handling.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from src.nodes.blocks.base import BaseBlock
from src.nodes.graphics_connection import GraphicsConnection


class ExecutionStatus(Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Execution result container."""

    status: ExecutionStatus
    executed_blocks: int = 0
    total_blocks: int = 0
    errors: List[Dict[str, Any]] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.errors is None:
            self.errors = []
        if self.context is None:
            self.context = {}


class WorkflowExecutor:
    """Workflow execution engine."""

    def __init__(self, blocks: List[BaseBlock], connections: List[GraphicsConnection]) -> None:
        """Initialize executor.

        Args:
            blocks: List of workflow blocks
            connections: List of connections between blocks
        """
        self.blocks = blocks
        self.connections = connections

        # Execution context
        self.context: Dict[str, Any] = {
            "variables": {},
            "loop_state": {},
            "control_flow": {},
        }

        # Execution state
        self.status = ExecutionStatus.PENDING
        self.executed_blocks: Set[BaseBlock] = set()
        self.errors: List[Dict[str, Any]] = []
        self._cancelled = False

        # Build execution graph
        self._graph: Dict[BaseBlock, List[tuple[int, BaseBlock]]] = {}
        self._build_graph()

    def _build_graph(self) -> None:
        """Build execution graph from blocks and connections."""
        # Initialize graph with all blocks
        for block in self.blocks:
            self._graph[block] = []

        # Add connections
        for connection in self.connections:
            source_block = self._find_block_by_graphics_node(connection.start_socket.parent_node)
            target_block = self._find_block_by_graphics_node(connection.end_socket.parent_node)

            if source_block and target_block:
                # Store output index with target block
                output_index = connection.start_socket.index
                self._graph[source_block].append((output_index, target_block))

        logger.info(f"Built execution graph with {len(self.blocks)} blocks")

    def _find_block_by_graphics_node(self, graphics_node) -> Optional[BaseBlock]:
        """Find block by graphics node.

        Args:
            graphics_node: Graphics node to search for

        Returns:
            Block if found, None otherwise
        """
        for block in self.blocks:
            if block.graphics_node == graphics_node:
                return block
        return None

    def _find_start_block(self) -> Optional[BaseBlock]:
        """Find starting block (block with no inputs).

        Returns:
            Start block if found, None otherwise
        """
        # Find blocks that are not targets of any connection
        target_blocks = set()
        for connections in self._graph.values():
            for _, target in connections:
                target_blocks.add(target)

        # Start block is one that's not a target
        for block in self.blocks:
            if block not in target_blocks:
                return block

        # If all blocks are targets (circular), return first block
        return self.blocks[0] if self.blocks else None

    async def execute(self, browser: Any) -> ExecutionResult:
        """Execute workflow.

        Args:
            browser: Browser instance for automation

        Returns:
            Execution result
        """
        try:
            self.status = ExecutionStatus.RUNNING
            self.context["browser"] = browser
            self.executed_blocks.clear()
            self.errors.clear()

            logger.info("Starting workflow execution")

            # Find start block
            start_block = self._find_start_block()
            if not start_block:
                raise Exception("No start block found")

            # Execute from start
            await self._execute_block(start_block)

            # Check status
            if self._cancelled:
                self.status = ExecutionStatus.CANCELLED
            elif self.errors:
                self.status = ExecutionStatus.FAILED
            else:
                self.status = ExecutionStatus.COMPLETED

            logger.info(
                f"Workflow execution {self.status.value}: "
                f"{len(self.executed_blocks)}/{len(self.blocks)} blocks"
            )

            return ExecutionResult(
                status=self.status,
                executed_blocks=len(self.executed_blocks),
                total_blocks=len(self.blocks),
                errors=self.errors,
                context=self.context,
            )

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            self.status = ExecutionStatus.FAILED
            self.errors.append({"block": "executor", "error": str(e)})

            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                executed_blocks=len(self.executed_blocks),
                total_blocks=len(self.blocks),
                errors=self.errors,
                context=self.context,
            )

    async def _execute_block(
        self, block: BaseBlock, loop_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute single block and follow connections.

        Args:
            block: Block to execute
            loop_context: Optional loop context for iteration
        """
        if self._cancelled:
            return

        # Check if already executed (avoid infinite loops)
        if block in self.executed_blocks and block.block_type != "condition":
            logger.debug(f"Block already executed: {block.title}")
            return

        try:
            logger.info(f"Executing block: {block.title}")

            # Reset block state
            block.reset_execution()

            # Execute block
            result = await block.execute(self.context)

            # Mark as executed
            self.executed_blocks.add(block)

            # Handle control flow
            if self.context.get("control_flow", {}).get("break"):
                logger.info("Break detected, exiting loop")
                return

            if self.context.get("control_flow", {}).get("continue"):
                logger.info("Continue detected, skipping to next iteration")
                self.context["control_flow"]["continue"] = False
                return

            # Get next blocks based on result
            next_blocks = self._get_next_blocks(block, result)

            # Handle special block types
            if block.block_type == "condition" and block.title == "Loop":
                await self._execute_loop(block, next_blocks, result)
            else:
                # Execute next blocks
                for next_block in next_blocks:
                    await self._execute_block(next_block, loop_context)

        except Exception as e:
            logger.error(f"Block execution failed: {block.title}: {e}")
            self.errors.append({"block": block.title, "error": str(e)})

            # Check if we should continue on error
            if not self.context.get("continue_on_error", False):
                raise

    async def _execute_loop(
        self, loop_block: BaseBlock, next_blocks: List[BaseBlock], loop_result: Dict[str, Any]
    ) -> None:
        """Execute loop block with proper iteration.

        Args:
            loop_block: Loop block
            next_blocks: Next blocks (body and exit)
            loop_result: Loop initialization result
        """
        loop_id = loop_result.get("loop_id")
        loop_state = self.context["loop_state"].get(loop_id)

        if not loop_state:
            logger.error("Loop state not found")
            return

        items = loop_state["items"]
        iterator_name = loop_state["iterator_name"]

        # Get body and exit blocks
        body_block = next_blocks[0] if len(next_blocks) > 0 else None
        exit_block = next_blocks[1] if len(next_blocks) > 1 else None

        # If no items, go to exit
        if not items:
            if exit_block:
                await self._execute_block(exit_block)
            return

        # Iterate through items
        for index, item in enumerate(items):
            if self._cancelled:
                break

            logger.info(f"Loop iteration {index + 1}/{len(items)}")

            # Update loop state
            loop_state["current_index"] = index
            if "variables" not in self.context:
                self.context["variables"] = {}
            self.context["variables"][iterator_name] = item

            # Clear control flow flags
            if "control_flow" in self.context:
                self.context["control_flow"]["break"] = False
                self.context["control_flow"]["continue"] = False

            # Execute loop body
            if body_block:
                await self._execute_block(body_block, loop_state)

            # Check for break
            if self.context.get("control_flow", {}).get("break"):
                logger.info("Breaking out of loop")
                self.context["control_flow"]["break"] = False
                break

            # Check for continue (already handled in body execution)

        # Execute exit block after loop completes
        if exit_block:
            await self._execute_block(exit_block)

    def _get_next_blocks(self, block: BaseBlock, result: Dict[str, Any]) -> List[BaseBlock]:
        """Get next blocks to execute based on block result.

        Args:
            block: Current block
            result: Execution result

        Returns:
            List of next blocks
        """
        connections = self._graph.get(block, [])

        # For blocks with multiple outputs (conditionals)
        if "branch_taken" in result:
            branch = result["branch_taken"]
            next_blocks = []

            # Get blocks connected to the specific output
            for output_index, target_block in connections:
                if output_index == branch:
                    next_blocks.append(target_block)

            return next_blocks

        # For regular blocks, return all connected blocks
        return [target for _, target in connections]

    def cancel(self) -> None:
        """Cancel workflow execution."""
        logger.info("Cancelling workflow execution")
        self._cancelled = True
        self.status = ExecutionStatus.CANCELLED

    def get_progress(self) -> float:
        """Get execution progress.

        Returns:
            Progress percentage (0-100)
        """
        if not self.blocks:
            return 0.0

        return (len(self.executed_blocks) / len(self.blocks)) * 100

    def get_context(self) -> Dict[str, Any]:
        """Get execution context.

        Returns:
            Execution context
        """
        return self.context.copy()

    def set_variable(self, name: str, value: Any) -> None:
        """Set context variable.

        Args:
            name: Variable name
            value: Variable value
        """
        if "variables" not in self.context:
            self.context["variables"] = {}
        self.context["variables"][name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get context variable.

        Args:
            name: Variable name
            default: Default value if not found

        Returns:
            Variable value
        """
        return self.context.get("variables", {}).get(name, default)
