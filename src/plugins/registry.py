"""
Plugin registry for OctoMaster Pro.

Central registry for managing plugin lifecycle and access.
"""

from typing import Dict, List, Optional, Type
from loguru import logger
from src.plugins.base import PluginBase


class PluginRegistry:
    """Central plugin registry."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_types: Dict[str, List[str]] = {
            "block": [],
            "integration": [],
            "theme": [],
            "exporter": [],
            "datasource": [],
        }
        self._initialized = True
        logger.info("PluginRegistry initialized")

    def register(self, plugin: PluginBase) -> bool:
        """Register plugin.

        Args:
            plugin: Plugin instance

        Returns:
            True if successful
        """
        if plugin.name in self.plugins:
            logger.warning(f"Plugin already registered: {plugin.name}")
            return False

        self.plugins[plugin.name] = plugin

        # Categorize plugin
        plugin_type = plugin.__class__.__bases__[0].__name__.lower().replace("plugin", "")
        if plugin_type in self.plugin_types:
            self.plugin_types[plugin_type].append(plugin.name)

        logger.info(f"Registered plugin: {plugin.name}")
        return True

    def unregister(self, plugin_name: str) -> bool:
        """Unregister plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if successful
        """
        if plugin_name not in self.plugins:
            return False

        # Remove from type lists
        for type_list in self.plugin_types.values():
            if plugin_name in type_list:
                type_list.remove(plugin_name)

        del self.plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        return True

    def get(self, plugin_name: str) -> Optional[PluginBase]:
        """Get plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)

    def get_all(self) -> List[PluginBase]:
        """Get all registered plugins.

        Returns:
            List of plugins
        """
        return list(self.plugins.values())

    def get_by_type(self, plugin_type: str) -> List[PluginBase]:
        """Get plugins by type.

        Args:
            plugin_type: Type of plugins

        Returns:
            List of matching plugins
        """
        plugin_names = self.plugin_types.get(plugin_type, [])
        return [self.plugins[name] for name in plugin_names if name in self.plugins]

    def get_enabled(self) -> List[PluginBase]:
        """Get all enabled plugins.

        Returns:
            List of enabled plugins
        """
        return [p for p in self.plugins.values() if p.enabled]

    def clear(self) -> None:
        """Clear all registered plugins."""
        self.plugins.clear()
        for type_list in self.plugin_types.values():
            type_list.clear()
        logger.info("Plugin registry cleared")
