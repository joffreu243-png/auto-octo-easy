"""
Plugin manager for OctoMaster Pro.

Handles plugin discovery, loading, and lifecycle management.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
import json

from loguru import logger

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


class PluginManager:
    """Manages plugins."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugins
        """
        if plugins_dir is None:
            plugins_dir = Path.cwd() / "plugins"

        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}

        # Ensure plugins directory exists
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins.

        Returns:
            List of plugin IDs
        """
        discovered = []

        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return discovered

        # Look for plugin directories
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Check for plugin.json metadata file
            metadata_file = plugin_dir / "plugin.json"
            if not metadata_file.exists():
                continue

            try:
                # Load metadata
                with open(metadata_file) as f:
                    metadata_dict = json.load(f)

                metadata = PluginMetadata(**metadata_dict)
                discovered.append(metadata.id)

                logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")

            except Exception as e:
                logger.error(f"Error loading plugin metadata from {plugin_dir}: {e}")

        return discovered

    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if successful
        """
        try:
            plugin_dir = self.plugins_dir / plugin_id

            if not plugin_dir.exists():
                logger.error(f"Plugin directory not found: {plugin_dir}")
                return False

            # Load metadata
            metadata_file = plugin_dir / "plugin.json"
            with open(metadata_file) as f:
                metadata_dict = json.load(f)

            metadata = PluginMetadata(**metadata_dict)

            # Check if already loaded
            if plugin_id in self.plugins:
                logger.warning(f"Plugin already loaded: {plugin_id}")
                return True

            # Load plugin module
            main_file = plugin_dir / "main.py"
            if not main_file.exists():
                logger.error(f"Plugin main.py not found: {main_file}")
                return False

            # Import plugin module
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", main_file)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin module: {main_file}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{plugin_id}"] = module
            spec.loader.exec_module(module)

            # Get plugin class (should be named 'PluginClass')
            if not hasattr(module, "PluginClass"):
                logger.error(f"Plugin class not found in {main_file}")
                return False

            plugin_class = getattr(module, "PluginClass")

            # Instantiate plugin
            plugin = plugin_class(metadata)

            # Initialize
            if not plugin.initialize():
                logger.error(f"Plugin initialization failed: {plugin_id}")
                return False

            plugin._initialized = True

            # Activate if enabled
            if metadata.enabled:
                if not plugin.activate():
                    logger.error(f"Plugin activation failed: {plugin_id}")
                    return False
                plugin._active = True

            # Store plugin
            self.plugins[plugin_id] = plugin
            self._plugin_classes[plugin_id] = plugin_class

            logger.info(f"Loaded plugin: {metadata.name} v{metadata.version}")
            return True

        except Exception as e:
            logger.exception(f"Error loading plugin {plugin_id}: {e}")
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if successful
        """
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_id}")
            return False

        try:
            plugin = self.plugins[plugin_id]

            # Deactivate if active
            if plugin.is_active:
                plugin.deactivate()
                plugin._active = False

            # Cleanup
            plugin.cleanup()

            # Remove from loaded plugins
            del self.plugins[plugin_id]
            if plugin_id in self._plugin_classes:
                del self._plugin_classes[plugin_id]

            logger.info(f"Unloaded plugin: {plugin_id}")
            return True

        except Exception as e:
            logger.exception(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if successful
        """
        self.unload_plugin(plugin_id)
        return self.load_plugin(plugin_id)

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a loaded plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Plugin type

        Returns:
            List of plugins
        """
        return [
            plugin
            for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]

    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if successful
        """
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not loaded: {plugin_id}")
            return False

        plugin = self.plugins[plugin_id]

        if plugin.is_active:
            logger.warning(f"Plugin already active: {plugin_id}")
            return True

        try:
            if plugin.activate():
                plugin._active = True
                plugin.metadata.enabled = True
                logger.info(f"Enabled plugin: {plugin_id}")
                return True
            else:
                logger.error(f"Plugin activation failed: {plugin_id}")
                return False

        except Exception as e:
            logger.exception(f"Error enabling plugin {plugin_id}: {e}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if successful
        """
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not loaded: {plugin_id}")
            return False

        plugin = self.plugins[plugin_id]

        if not plugin.is_active:
            logger.warning(f"Plugin already inactive: {plugin_id}")
            return True

        try:
            if plugin.deactivate():
                plugin._active = False
                plugin.metadata.enabled = False
                logger.info(f"Disabled plugin: {plugin_id}")
                return True
            else:
                logger.error(f"Plugin deactivation failed: {plugin_id}")
                return False

        except Exception as e:
            logger.exception(f"Error disabling plugin {plugin_id}: {e}")
            return False

    def load_all_plugins(self) -> int:
        """
        Discover and load all plugins.

        Returns:
            Number of plugins loaded
        """
        plugin_ids = self.discover_plugins()
        loaded_count = 0

        for plugin_id in plugin_ids:
            if self.load_plugin(plugin_id):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(plugin_ids)} plugins")
        return loaded_count

    def unload_all_plugins(self):
        """Unload all plugins."""
        plugin_ids = list(self.plugins.keys())

        for plugin_id in plugin_ids:
            self.unload_plugin(plugin_id)

        logger.info("Unloaded all plugins")

    def get_stats(self) -> Dict[str, int]:
        """
        Get plugin statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "total": len(self.plugins),
            "active": sum(1 for p in self.plugins.values() if p.is_active),
            "inactive": sum(1 for p in self.plugins.values() if not p.is_active),
        }

        # Count by type
        for plugin_type in PluginType:
            count = len(self.get_plugins_by_type(plugin_type))
            stats[f"type_{plugin_type.value}"] = count

        return stats

    def list_plugins(self) -> List[Dict[str, str]]:
        """
        List all loaded plugins.

        Returns:
            List of plugin info dictionaries
        """
        return [
            {
                "id": plugin.metadata.id,
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "type": plugin.metadata.plugin_type.value,
                "author": plugin.metadata.author,
                "active": plugin.is_active,
            }
            for plugin in self.plugins.values()
        ]
