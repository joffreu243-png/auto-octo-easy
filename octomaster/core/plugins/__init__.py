"""
Plugin system for OctoMaster Pro.

Allows extending functionality with custom blocks, integrations, themes, and tools.
"""

from octomaster.core.plugins.plugin import (
    Plugin,
    PluginType,
    PluginMetadata,
    BlockPlugin,
    IntegrationPlugin,
    ThemePlugin,
    ToolPlugin,
    ExporterPlugin,
)
from octomaster.core.plugins.manager import PluginManager

__all__ = [
    "Plugin",
    "PluginType",
    "PluginMetadata",
    "BlockPlugin",
    "IntegrationPlugin",
    "ThemePlugin",
    "ToolPlugin",
    "ExporterPlugin",
    "PluginManager",
]
