#!/usr/bin/env python3
"""
Example: Creating a workflow programmatically.

This example shows how to create a workflow using the OctoMaster Pro API.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType


def create_google_search_workflow():
    """Create a workflow that searches Google."""

    # Create workflow
    workflow = Workflow(name="Google Search Example")
    workflow.description = "Open Google and search for Python programming"

    # Block 1: Open Google
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "https://google.com")
    workflow.add_block(open_url)

    # Block 2: Wait for search box
    wait_search = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_search.set_parameter("selector", "input[name='q']")
    wait_search.set_parameter("timeout", 5000)
    workflow.add_block(wait_search)

    # Block 3: Type search query
    type_query = Block(type=BlockType.TYPE_TEXT)
    type_query.set_parameter("selector", "input[name='q']")
    type_query.set_parameter("text", "Python programming")
    workflow.add_block(type_query)

    # Block 4: Click search button
    click_search = Block(type=BlockType.CLICK)
    click_search.set_parameter("selector", "input[name='btnK']")
    workflow.add_block(click_search)

    # Block 5: Wait for results
    wait_results = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_results.set_parameter("selector", "#search")
    workflow.add_block(wait_results)

    # Block 6: Take screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "google_results.png")
    workflow.add_block(screenshot)

    # Connect blocks sequentially
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    return workflow


def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - Workflow Example")
    print("=" * 60)

    # Create workflow
    workflow = create_google_search_workflow()
    print(f"\nCreated workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Blocks: {len(workflow.blocks)}")
    print(f"Connections: {len(workflow.connections)}")

    # Validate workflow
    is_valid, errors = workflow.validate()
    print(f"\nWorkflow valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")

    # Save workflow
    output_path = Path(__file__).parent / "google_search.workflow"
    workflow.save(output_path)
    print(f"\nWorkflow saved to: {output_path}")

    # Export as Python code
    python_code = workflow.export_to_python()
    code_path = Path(__file__).parent / "google_search.py"
    with open(code_path, "w") as f:
        f.write(python_code)
    print(f"Python code exported to: {code_path}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
