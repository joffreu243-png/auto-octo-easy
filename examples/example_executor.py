#!/usr/bin/env python3
"""
Example: Using the Workflow Executor.

This example shows how to execute a workflow using the executor.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType
from octomaster.automation.executor import WorkflowExecutor


async def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - Workflow Executor Example")
    print("=" * 60)

    # Create a simple workflow
    workflow = Workflow(name="Example Workflow")
    workflow.description = "Simple example workflow that opens Google and takes a screenshot"

    # Block 1: Open Google
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "https://google.com")
    workflow.add_block(open_url)

    # Block 2: Wait for page load
    wait_load = Block(type=BlockType.WAIT_FOR_LOAD)
    workflow.add_block(wait_load)

    # Block 3: Take screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "google_homepage.png")
    workflow.add_block(screenshot)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    print(f"\nWorkflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Blocks: {len(workflow.blocks)}")
    print(f"Connections: {len(workflow.connections)}")

    # Validate workflow
    is_valid, errors = workflow.validate()
    if not is_valid:
        print("\nValidation errors:")
        for error in errors:
            print(f"  - {error}")
        return

    print("\nValidation: ✓ Passed")

    # Create executor
    executor = WorkflowExecutor(workflow)

    # Add callbacks for events
    def on_execution_started(wf):
        print(f"\n🚀 Execution started: {wf.name}")

    def on_block_started(block):
        print(f"  ▶️  Executing: {block.name} ({block.type.value})")

    def on_block_completed(block, result):
        print(f"  ✅ Completed: {block.name} ({result.duration:.2f}s)")

    def on_block_failed(block, result):
        print(f"  ❌ Failed: {block.name} - {result.error}")

    def on_execution_completed(results):
        print(f"\n✅ Execution completed!")
        print(f"Total blocks executed: {len(results)}")

    def on_execution_failed(error):
        print(f"\n❌ Execution failed: {error}")

    # Register callbacks
    executor.add_callback("execution_started", on_execution_started)
    executor.add_callback("block_started", on_block_started)
    executor.add_callback("block_completed", on_block_completed)
    executor.add_callback("block_failed", on_block_failed)
    executor.add_callback("execution_completed", on_execution_completed)
    executor.add_callback("execution_failed", on_execution_failed)

    # Execute workflow
    print("\n" + "=" * 60)
    success = await executor.execute(headless=True)

    # Show stats
    stats = executor.get_stats()
    print("\n" + "=" * 60)
    print("Execution Statistics:")
    print("=" * 60)
    print(f"Status: {stats['status']}")
    print(f"Duration: {stats['duration']:.2f}s")
    print(f"Total blocks: {stats['total_blocks']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")

    if stats['variables']:
        print(f"\nVariables:")
        for name, value in stats['variables'].items():
            print(f"  {name} = {value}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
