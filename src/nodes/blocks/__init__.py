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
from src.nodes.blocks.wait import (
    WaitBlock,
    WaitForElementBlock,
    WaitForNavigationBlock,
    WaitForSelectorBlock,
)
from src.nodes.blocks.data import (
    ExtractTextBlock,
    ExtractAttributeBlock,
    SetVariableBlock,
    GetVariableBlock,
    ExtractMultipleBlock,
)
from src.nodes.blocks.conditions import (
    IfBlock,
    LoopBlock,
    SwitchBlock,
    BreakBlock,
    ContinueBlock,
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
    # Wait
    "WaitBlock",
    "WaitForElementBlock",
    "WaitForNavigationBlock",
    "WaitForSelectorBlock",
    # Data
    "ExtractTextBlock",
    "ExtractAttributeBlock",
    "SetVariableBlock",
    "GetVariableBlock",
    "ExtractMultipleBlock",
    # Conditions
    "IfBlock",
    "LoopBlock",
    "SwitchBlock",
    "BreakBlock",
    "ContinueBlock",
]
