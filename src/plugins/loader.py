"""
Plugin loader for OctoMaster Pro.

Dynamically loads and manages plugins from directories.
"""

from typing import List, Dict, Any, Optional, Type
from pathlib import Path
import importlib.util
import sys
from loguru import logger

from src.plugins.base import PluginBase


class PluginLoader:
    """Dynamic plugin loader."""

    def __init__(self, plugins_dir: Path):
        """Initialize plugin loader.

        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        self.loaded_plugins: Dict[str, PluginBase] = {}
        self.plugin_modules: Dict[str, Any] = {}

        logger.info(f"PluginLoader initialized: {plugins_dir}")

    def discover_plugins(self) -> List[Path]:
        """Discover plugin files in directory.

        Returns:
            List of plugin file paths
        """
        plugins = []

        # Look for Python files
        for plugin_file in self.plugins_dir.rglob("*.py"):
            # Skip __init__.py and __pycache__
            if plugin_file.name.startswith("__"):
                continue

            plugins.append(plugin_file)

        logger.info(f"Discovered {len(plugins)} plugin files")
        return plugins

    def load_plugin(
        self, plugin_path: Path, app: Optional[Any] = None
    ) -> Optional[PluginBase]:
        """Load single plugin from file.

        Args:
            plugin_path: Path to plugin file
            app: Application instance

        Returns:
            Loaded plugin instance or None
        """
        try:
            # Create module name from file path
            module_name = f"plugins.{plugin_path.stem}"

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to load spec for {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find plugin class in module
            plugin_class = None

            for name in dir(module):
                obj = getattr(module, name)

                # Check if it's a plugin class (not PluginBase itself)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, PluginBase)
                    and obj is not PluginBase
                ):
                    plugin_class = obj
                    break

            if not plugin_class:
                logger.error(f"No plugin class found in {plugin_path}")
                return None

            # Instantiate plugin
            plugin = plugin_class(app)

            # Call on_load
            plugin.on_load()

            # Store plugin
            self.loaded_plugins[plugin.name] = plugin
            self.plugin_modules[plugin.name] = module

            logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            return plugin

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return None

    def load_all_plugins(self, app: Optional[Any] = None) -> int:
        """Load all discovered plugins.

        Args:
            app: Application instance

        Returns:
            Number of successfully loaded plugins
        """
        plugins = self.discover_plugins()
        loaded_count = 0

        for plugin_path in plugins:
            plugin = self.load_plugin(plugin_path, app)
            if plugin:
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(plugins)} plugins")
        return loaded_count

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if successful
        """
        plugin = self.loaded_plugins.get(plugin_name)

        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False

        if plugin.enabled:
            logger.warning(f"Plugin already enabled: {plugin_name}")
            return True

        try:
            # Check dependencies
            if not self._check_dependencies(plugin):
                logger.error(f"Plugin dependencies not met: {plugin_name}")
                return False

            # Check conflicts
            if not self._check_conflicts(plugin):
                logger.error(f"Plugin conflicts detected: {plugin_name}")
                return False

            # Enable plugin
            plugin.on_enable()
            plugin.enabled = True

            logger.info(f"Enabled plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if successful
        """
        plugin = self.loaded_plugins.get(plugin_name)

        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False

        if not plugin.enabled:
            logger.warning(f"Plugin already disabled: {plugin_name}")
            return True

        try:
            plugin.on_disable()
            plugin.enabled = False

            logger.info(f"Disabled plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if successful
        """
        plugin = self.loaded_plugins.get(plugin_name)

        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False

        try:
            # Disable first if enabled
            if plugin.enabled:
                self.disable_plugin(plugin_name)

            # Call on_unload
            plugin.on_unload()

            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]

            # Remove module
            if plugin_name in self.plugin_modules:
                module_name = self.plugin_modules[plugin_name].__name__
                if module_name in sys.modules:
                    del sys.modules[module_name]
                del self.plugin_modules[plugin_name]

            logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get loaded plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.loaded_plugins.get(plugin_name)

    def get_all_plugins(self) -> List[PluginBase]:
        """Get all loaded plugins.

        Returns:
            List of loaded plugins
        """
        return list(self.loaded_plugins.values())

    def get_enabled_plugins(self) -> List[PluginBase]:
        """Get all enabled plugins.

        Returns:
            List of enabled plugins
        """
        return [p for p in self.loaded_plugins.values() if p.enabled]

    def _check_dependencies(self, plugin: PluginBase) -> bool:
        """Check if plugin dependencies are met.

        Args:
            plugin: Plugin to check

        Returns:
            True if all dependencies met
        """
        for required in plugin.requires:
            if required not in self.loaded_plugins:
                logger.error(f"Required plugin not loaded: {required}")
                return False

            if not self.loaded_plugins[required].enabled:
                logger.error(f"Required plugin not enabled: {required}")
                return False

        return True

    def _check_conflicts(self, plugin: PluginBase) -> bool:
        """Check for plugin conflicts.

        Args:
            plugin: Plugin to check

        Returns:
            True if no conflicts
        """
        for conflict in plugin.conflicts:
            if conflict in self.loaded_plugins:
                if self.loaded_plugins[conflict].enabled:
                    logger.error(f"Conflicting plugin enabled: {conflict}")
                    return False

        return True

    def reload_plugin(self, plugin_name: str, app: Optional[Any] = None) -> bool:
        """Reload plugin (unload and load again).

        Args:
            plugin_name: Plugin name
            app: Application instance

        Returns:
            True if successful
        """
        # Get plugin path before unloading
        plugin = self.loaded_plugins.get(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False

        # Find plugin file
        plugin_path = None
        for p in self.discover_plugins():
            if p.stem == plugin_name or plugin_name in str(p):
                plugin_path = p
                break

        if not plugin_path:
            logger.error(f"Plugin file not found: {plugin_name}")
            return False

        # Unload
        if not self.unload_plugin(plugin_name):
            return False

        # Load again
        new_plugin = self.load_plugin(plugin_path, app)

        if new_plugin:
            logger.info(f"Reloaded plugin: {plugin_name}")
            return True

        return False

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin info dictionary or None
        """
        plugin = self.loaded_plugins.get(plugin_name)

        if not plugin:
            return None

        return plugin.get_info()

    def get_all_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information for all plugins.

        Returns:
            List of plugin info dictionaries
        """
        return [p.get_info() for p in self.loaded_plugins.values()]
