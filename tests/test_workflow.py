"""
Tests for Workflow class.
"""

import pytest
from pathlib import Path
from octomaster.core.workflow import Workflow, Connection
from octomaster.core.block import Block, BlockType


def test_workflow_creation():
    """Test creating a workflow."""
    workflow = Workflow(name="Test Workflow")
    assert workflow.name == "Test Workflow"
    assert len(workflow.blocks) == 0
    assert len(workflow.connections) == 0


def test_add_block():
    """Test adding blocks to workflow."""
    workflow = Workflow()
    block = Block(type=BlockType.CLICK)

    workflow.add_block(block)

    assert len(workflow.blocks) == 1
    assert workflow.blocks[0] == block


def test_remove_block():
    """Test removing blocks from workflow."""
    workflow = Workflow()
    block1 = Block(type=BlockType.CLICK)
    block2 = Block(type=BlockType.TYPE_TEXT)

    workflow.add_block(block1)
    workflow.add_block(block2)

    workflow.remove_block(block1.id)

    assert len(workflow.blocks) == 1
    assert workflow.blocks[0] == block2


def test_connect_blocks():
    """Test connecting blocks."""
    workflow = Workflow()
    block1 = Block(type=BlockType.OPEN_URL)
    block2 = Block(type=BlockType.CLICK)

    workflow.add_block(block1)
    workflow.add_block(block2)

    connection = workflow.connect_blocks(block1.id, block2.id)

    assert len(workflow.connections) == 1
    assert connection.source_block_id == block1.id
    assert connection.target_block_id == block2.id


def test_get_next_blocks():
    """Test getting next blocks."""
    workflow = Workflow()
    block1 = Block(type=BlockType.OPEN_URL)
    block2 = Block(type=BlockType.CLICK)
    block3 = Block(type=BlockType.TYPE_TEXT)

    workflow.add_block(block1)
    workflow.add_block(block2)
    workflow.add_block(block3)

    workflow.connect_blocks(block1.id, block2.id)
    workflow.connect_blocks(block1.id, block3.id)

    next_blocks = workflow.get_next_blocks(block1.id)

    assert len(next_blocks) == 2
    assert block2 in next_blocks
    assert block3 in next_blocks


def test_validate_workflow():
    """Test workflow validation."""
    # Empty workflow is invalid
    workflow = Workflow()
    is_valid, errors = workflow.validate()
    assert not is_valid
    assert len(errors) > 0

    # Workflow with blocks is valid
    workflow.add_block(Block(type=BlockType.OPEN_URL))
    is_valid, errors = workflow.validate()
    assert is_valid
    assert len(errors) == 0


def test_workflow_serialization():
    """Test workflow to/from dict."""
    workflow = Workflow(name="Test Workflow")
    block = Block(type=BlockType.CLICK)
    workflow.add_block(block)

    # To dict
    data = workflow.to_dict()
    assert data["name"] == "Test Workflow"
    assert len(data["blocks"]) == 1

    # From dict
    workflow2 = Workflow.from_dict(data)
    assert workflow2.name == workflow.name
    assert len(workflow2.blocks) == len(workflow.blocks)


def test_workflow_save_load(tmp_path):
    """Test saving and loading workflow."""
    workflow = Workflow(name="Test Workflow")
    block = Block(type=BlockType.OPEN_URL)
    block.set_parameter("url", "https://example.com")
    workflow.add_block(block)

    # Save
    file_path = tmp_path / "test.workflow"
    workflow.save(file_path)
    assert file_path.exists()

    # Load
    loaded_workflow = Workflow.load(file_path)
    assert loaded_workflow.name == workflow.name
    assert len(loaded_workflow.blocks) == len(workflow.blocks)


def test_export_to_python():
    """Test exporting workflow to Python code."""
    workflow = Workflow(name="Test Workflow")

    block1 = Block(type=BlockType.OPEN_URL)
    block1.set_parameter("url", "https://google.com")
    workflow.add_block(block1)

    block2 = Block(type=BlockType.CLICK)
    block2.set_parameter("selector", "button")
    workflow.add_block(block2)

    workflow.connect_blocks(block1.id, block2.id)

    code = workflow.export_to_python()

    assert "def main():" in code
    assert "playwright" in code
    assert "https://google.com" in code
