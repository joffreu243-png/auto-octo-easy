"""
Workflow blocks for visual node editor.

Provides various types of blocks for browser automation workflows.
"""

from src.nodes.blocks.base import BaseBlock
from src.nodes.blocks.navigation import (
    OpenURLBlock,
    BackBlock,
    ForwardBlock,
    RefreshBlock,
    NewTabBlock,
    CloseTabBlock,
)
from src.nodes.blocks.actions import (
    ClickBlock,
    TypeTextBlock,
    FillBlock,
    SelectDropdownBlock,
    HoverBlock,
    ScrollBlock,
    ScreenshotBlock,
)

__all__ = [
    "BaseBlock",
    # Navigation
    "OpenURLBlock",
    "BackBlock",
    "ForwardBlock",
    "RefreshBlock",
    "NewTabBlock",
    "CloseTabBlock",
    # Actions
    "ClickBlock",
    "TypeTextBlock",
    "FillBlock",
    "SelectDropdownBlock",
    "HoverBlock",
    "ScrollBlock",
    "ScreenshotBlock",
]
