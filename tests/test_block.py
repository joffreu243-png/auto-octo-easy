"""
Tests for Block class.
"""

import pytest
from octomaster.core.block import Block, BlockType


def test_block_creation():
    """Test creating a block."""
    block = Block(type=BlockType.CLICK)
    assert block.type == BlockType.CLICK
    assert block.enabled is True
    assert block.breakpoint is False


def test_block_name_auto_generation():
    """Test automatic block name generation."""
    block = Block(type=BlockType.OPEN_URL)
    assert block.name == "Open Url"


def test_block_parameters():
    """Test getting and setting parameters."""
    block = Block(type=BlockType.TYPE_TEXT)

    block.set_parameter("selector", "input#username")
    block.set_parameter("text", "test_user")

    assert block.get_parameter("selector") == "input#username"
    assert block.get_parameter("text") == "test_user"
    assert block.get_parameter("nonexistent", "default") == "default"


def test_block_category_assignment():
    """Test automatic category assignment."""
    nav_block = Block(type=BlockType.OPEN_URL)
    assert nav_block.category == "Navigation"

    action_block = Block(type=BlockType.CLICK)
    assert action_block.category == "Actions"

    wait_block = Block(type=BlockType.WAIT_TIME)
    assert wait_block.category == "Waits"


def test_block_serialization():
    """Test block to/from dict."""
    block = Block(type=BlockType.CLICK)
    block.set_parameter("selector", "button.submit")
    block.x = 100
    block.y = 200

    # To dict
    data = block.to_dict()
    assert data["type"] == "click"
    assert data["parameters"]["selector"] == "button.submit"
    assert data["position"]["x"] == 100
    assert data["position"]["y"] == 200

    # From dict
    block2 = Block.from_dict(data)
    assert block2.type == block.type
    assert block2.get_parameter("selector") == block.get_parameter("selector")
    assert block2.x == block.x
    assert block2.y == block.y


def test_block_clone():
    """Test cloning a block."""
    block = Block(type=BlockType.TYPE_TEXT)
    block.set_parameter("selector", "input")
    block.x = 50
    block.y = 50

    cloned = block.clone()

    assert cloned.id != block.id  # Different ID
    assert cloned.type == block.type
    assert cloned.get_parameter("selector") == block.get_parameter("selector")
    assert cloned.x == block.x + 20  # Offset position
    assert cloned.y == block.y + 20
