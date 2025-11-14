"""
Plugin system for OctoMaster Pro.

Provides extensible plugin architecture for adding custom functionality.
"""

from src.plugins.base import PluginBase, BlockPlugin, IntegrationPlugin, ThemePlugin
from src.plugins.loader import PluginLoader
from src.plugins.registry import PluginRegistry
from src.plugins.api import PluginAPI

__all__ = [
    "PluginBase",
    "BlockPlugin",
    "IntegrationPlugin",
    "ThemePlugin",
    "PluginLoader",
    "PluginRegistry",
    "PluginAPI",
]
