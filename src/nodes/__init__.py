"""
Visual node editor module for OctoMaster Pro.

Complete node-based visual workflow editor with graphics nodes, connections,
and workflow blocks for browser automation.
"""

from src.nodes.scene import NodeScene
from src.nodes.graphics_node import GraphicsNode, Socket
from src.nodes.graphics_connection import GraphicsConnection
from src.nodes.blocks import *

__all__ = [
    "NodeScene",
    "GraphicsNode",
    "Socket",
    "GraphicsConnection",
    "BaseBlock",
    # Navigation blocks
    "OpenURLBlock",
    "BackBlock",
    "ForwardBlock",
    "RefreshBlock",
    "NewTabBlock",
    "CloseTabBlock",
    # Action blocks
    "ClickBlock",
    "TypeTextBlock",
    "FillBlock",
    "SelectDropdownBlock",
    "HoverBlock",
    "ScrollBlock",
    "ScreenshotBlock",
]
