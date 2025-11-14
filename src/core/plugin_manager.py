"""
Plugin manager for OctoMaster Pro.

This module provides plugin management functionality, allowing dynamic loading
and unloading of plugins to extend application functionality.
"""

from pathlib import Path
from typing import Optional, Any
import importlib.util
import inspect
from abc import ABC, abstractmethod
from loguru import logger
from src.core.exceptions import PluginError
from src.core.events import EventBus, EventType, emit_event


class Plugin(ABC):
    """Base class for all plugins."""

    def __init__(self) -> None:
        """Initialize plugin."""
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.enabled = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        pass

    def get_info(self) -> dict[str, Any]:
        """
        Get plugin information.

        Returns:
            Plugin information dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "enabled": self.enabled,
        }


class PluginManager:
    """
    Plugin manager for loading and managing plugins.

    Provides functionality to discover, load, enable, and unload plugins.
    """

    def __init__(self, plugins_dir: Optional[Path] = None) -> None:
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugins_dir = plugins_dir or Path("plugins")
        self.plugins: dict[str, Plugin] = {}
        self._event_bus = EventBus()

    def discover_plugins(self) -> list[str]:
        """
        Discover available plugins in the plugins directory.

        Returns:
            List of plugin names
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []

        plugin_names: list[str] = []

        for plugin_path in self.plugins_dir.iterdir():
            if plugin_path.is_dir() and (plugin_path / "__init__.py").exists():
                plugin_names.append(plugin_path.name)
            elif plugin_path.is_file() and plugin_path.suffix == ".py":
                if plugin_path.stem != "__init__":
                    plugin_names.append(plugin_path.stem)

        logger.info(f"Discovered {len(plugin_names)} plugins: {plugin_names}")
        return plugin_names

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            True if loaded successfully, False otherwise

        Raises:
            PluginError: If plugin loading fails
        """
        try:
            # Check if already loaded
            if plugin_name in self.plugins:
                logger.warning(f"Plugin already loaded: {plugin_name}")
                return False

            # Find plugin file
            plugin_path = self.plugins_dir / plugin_name
            if plugin_path.is_dir():
                plugin_file = plugin_path / "__init__.py"
            else:
                plugin_file = self.plugins_dir / f"{plugin_name}.py"

            if not plugin_file.exists():
                raise PluginError(f"Plugin file not found: {plugin_file}", plugin_name=plugin_name)

            # Load module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if spec is None or spec.loader is None:
                raise PluginError(f"Failed to load plugin spec: {plugin_name}", plugin_name=plugin_name)

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Plugin subclass
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugin_class = obj
                    break

            if plugin_class is None:
                raise PluginError(
                    f"No Plugin subclass found in {plugin_name}",
                    plugin_name=plugin_name
                )

            # Instantiate plugin
            plugin_instance = plugin_class()
            self.plugins[plugin_name] = plugin_instance

            logger.info(f"Plugin loaded: {plugin_name}")
            emit_event(EventType.PLUGIN_LOADED, {"plugin_name": plugin_name})

            return True

        except Exception as e:
            error_msg = f"Failed to load plugin {plugin_name}: {e}"
            logger.error(error_msg)
            emit_event(EventType.PLUGIN_ERROR, {"plugin_name": plugin_name, "error": str(e)})
            raise PluginError(error_msg, plugin_name=plugin_name) from e

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        try:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                self.disable_plugin(plugin_name)

            del self.plugins[plugin_name]

            logger.info(f"Plugin unloaded: {plugin_name}")
            emit_event(EventType.PLUGIN_UNLOADED, {"plugin_name": plugin_name})

            return True

        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if enabled successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        plugin = self.plugins[plugin_name]
        if plugin.enabled:
            logger.info(f"Plugin already enabled: {plugin_name}")
            return True

        try:
            if plugin.initialize():
                plugin.enabled = True
                logger.info(f"Plugin enabled: {plugin_name}")
                return True
            else:
                logger.warning(f"Plugin initialization returned False: {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            emit_event(EventType.PLUGIN_ERROR, {"plugin_name": plugin_name, "error": str(e)})
            return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable an enabled plugin.

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if disabled successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        plugin = self.plugins[plugin_name]
        if not plugin.enabled:
            logger.info(f"Plugin already disabled: {plugin_name}")
            return True

        try:
            plugin.shutdown()
            plugin.enabled = False
            logger.info(f"Plugin disabled: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> dict[str, Plugin]:
        """
        Get all loaded plugins.

        Returns:
            Dictionary of plugin name to plugin instance
        """
        return self.plugins.copy()

    def get_enabled_plugins(self) -> dict[str, Plugin]:
        """
        Get all enabled plugins.

        Returns:
            Dictionary of enabled plugins
        """
        return {name: plugin for name, plugin in self.plugins.items() if plugin.enabled}

    def load_all_plugins(self) -> int:
        """
        Load all discovered plugins.

        Returns:
            Number of plugins loaded
        """
        plugin_names = self.discover_plugins()
        loaded_count = 0

        for plugin_name in plugin_names:
            try:
                if self.load_plugin(plugin_name):
                    loaded_count += 1
            except PluginError as e:
                logger.warning(f"Skipping plugin {plugin_name}: {e}")

        logger.info(f"Loaded {loaded_count}/{len(plugin_names)} plugins")
        return loaded_count

    def enable_all_plugins(self) -> int:
        """
        Enable all loaded plugins.

        Returns:
            Number of plugins enabled
        """
        enabled_count = 0

        for plugin_name in self.plugins:
            if self.enable_plugin(plugin_name):
                enabled_count += 1

        logger.info(f"Enabled {enabled_count}/{len(self.plugins)} plugins")
        return enabled_count

    def shutdown_all_plugins(self) -> None:
        """Shutdown all enabled plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.disable_plugin(plugin_name)

        logger.info("All plugins shut down")


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager(plugins_dir: Optional[Path] = None) -> PluginManager:
    """
    Get global plugin manager instance.

    Args:
        plugins_dir: Plugins directory (only used on first call)

    Returns:
        PluginManager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugins_dir)
    return _plugin_manager
