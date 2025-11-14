"""
Unit tests for plugin manager.

Tests the plugin system, loading, and management functionality.
"""

import pytest
from pathlib import Path
from src.core.plugin_manager import (
    Plugin,
    PluginManager,
    get_plugin_manager,
)
from src.core.exceptions import PluginError


class TestPlugin:
    """Tests for base Plugin class."""

    def test_cannot_instantiate_abstract_plugin(self):
        """Test that Plugin is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Plugin()  # Should raise TypeError

    def test_plugin_subclass(self):
        """Test creating Plugin subclass."""

        class TestPlugin(Plugin):
            def initialize(self) -> bool:
                self.initialized = True
                return True

            def shutdown(self) -> None:
                self.initialized = False

        plugin = TestPlugin()
        assert plugin.name == "TestPlugin"
        assert plugin.version == "1.0.0"
        assert plugin.enabled is False

    def test_plugin_get_info(self):
        """Test getting plugin information."""

        class InfoPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "TestPlugin"
                self.version = "2.0.0"
                self.description = "Test plugin"
                self.author = "Test Author"

            def initialize(self) -> bool:
                return True

            def shutdown(self) -> None:
                pass

        plugin = InfoPlugin()
        info = plugin.get_info()

        assert isinstance(info, dict)
        assert info["name"] == "TestPlugin"
        assert info["version"] == "2.0.0"
        assert info["description"] == "Test plugin"
        assert info["author"] == "Test Author"
        assert info["enabled"] is False


class TestPluginManager:
    """Tests for PluginManager class."""

    def test_initialization(self, tmp_path):
        """Test plugin manager initialization."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)

        assert manager.plugins_dir == plugins_dir
        assert isinstance(manager.plugins, dict)
        assert len(manager.plugins) == 0

    def test_default_plugins_directory(self):
        """Test default plugins directory."""
        manager = PluginManager()

        assert manager.plugins_dir == Path("plugins")

    def test_discover_plugins_empty_directory(self, tmp_path):
        """Test discovering plugins in empty directory."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)
        plugins = manager.discover_plugins()

        assert plugins == []

    def test_discover_plugins_with_files(self, tmp_path):
        """Test discovering plugins from Python files."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create some plugin files
        (plugins_dir / "plugin1.py").write_text("# Plugin 1")
        (plugins_dir / "plugin2.py").write_text("# Plugin 2")
        (plugins_dir / "__init__.py").write_text("# Init")

        manager = PluginManager(plugins_dir)
        plugins = manager.discover_plugins()

        assert "plugin1" in plugins
        assert "plugin2" in plugins
        # __init__ should not be listed as plugin
        assert "__init__" not in plugins

    def test_discover_plugins_with_directories(self, tmp_path):
        """Test discovering plugins from directories."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin directory with __init__.py
        plugin_dir = plugins_dir / "my_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "__init__.py").write_text("# My Plugin")

        manager = PluginManager(plugins_dir)
        plugins = manager.discover_plugins()

        assert "my_plugin" in plugins

    def test_discover_nonexistent_directory(self, tmp_path):
        """Test discovering plugins from nonexistent directory."""
        nonexistent_dir = tmp_path / "nonexistent"

        manager = PluginManager(nonexistent_dir)
        plugins = manager.discover_plugins()

        assert plugins == []

    def test_load_plugin_not_found_raises_error(self, tmp_path):
        """Test loading non-existent plugin raises error."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)

        with pytest.raises(PluginError, match="not found"):
            manager.load_plugin("nonexistent_plugin")

    def test_load_plugin_already_loaded(self, tmp_path):
        """Test loading already loaded plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create simple plugin
        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class TestPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)

        # Load first time
        result = manager.load_plugin("test_plugin")
        assert result is True

        # Try to load again
        result = manager.load_plugin("test_plugin")
        assert result is False  # Already loaded

    def test_get_plugin(self, tmp_path):
        """Test getting loaded plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin
        plugin_file = plugins_dir / "my_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class MyPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)
        manager.load_plugin("my_plugin")

        plugin = manager.get_plugin("my_plugin")
        assert plugin is not None
        assert plugin.name == "MyPlugin"

    def test_get_nonexistent_plugin(self, tmp_path):
        """Test getting non-existent plugin returns None."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)

        plugin = manager.get_plugin("nonexistent")
        assert plugin is None

    def test_get_all_plugins(self, tmp_path):
        """Test getting all loaded plugins."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)

        # Initially empty
        all_plugins = manager.get_all_plugins()
        assert len(all_plugins) == 0

    def test_get_enabled_plugins(self, tmp_path):
        """Test getting only enabled plugins."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin
        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class TestPlugin(Plugin):
    def initialize(self) -> bool:
        self.enabled = True
        return True

    def shutdown(self) -> None:
        self.enabled = False
""")

        manager = PluginManager(plugins_dir)
        manager.load_plugin("test_plugin")

        # Before enabling
        enabled = manager.get_enabled_plugins()
        assert len(enabled) == 0

        # Enable plugin
        manager.enable_plugin("test_plugin")

        # After enabling
        enabled = manager.get_enabled_plugins()
        assert len(enabled) == 1
        assert "test_plugin" in enabled

    def test_enable_plugin(self, tmp_path):
        """Test enabling a plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class TestPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)
        manager.load_plugin("test_plugin")

        result = manager.enable_plugin("test_plugin")
        assert result is True

        plugin = manager.get_plugin("test_plugin")
        assert plugin.enabled is True

    def test_enable_nonexistent_plugin(self, tmp_path):
        """Test enabling non-existent plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        manager = PluginManager(plugins_dir)

        result = manager.enable_plugin("nonexistent")
        assert result is False

    def test_disable_plugin(self, tmp_path):
        """Test disabling a plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class TestPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)
        manager.load_plugin("test_plugin")
        manager.enable_plugin("test_plugin")

        # Plugin should be enabled
        plugin = manager.get_plugin("test_plugin")
        assert plugin.enabled is True

        # Disable it
        result = manager.disable_plugin("test_plugin")
        assert result is True
        assert plugin.enabled is False

    def test_unload_plugin(self, tmp_path):
        """Test unloading a plugin."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from src.core.plugin_manager import Plugin

class TestPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)
        manager.load_plugin("test_plugin")

        # Plugin should be loaded
        assert "test_plugin" in manager.plugins

        # Unload it
        result = manager.unload_plugin("test_plugin")
        assert result is True

        # Should not be in plugins anymore
        assert "test_plugin" not in manager.plugins

    def test_shutdown_all_plugins(self, tmp_path):
        """Test shutting down all plugins."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create multiple plugins
        for i in range(3):
            plugin_file = plugins_dir / f"plugin{i}.py"
            plugin_file.write_text(f"""
from src.core.plugin_manager import Plugin

class Plugin{i}(Plugin):
    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass
""")

        manager = PluginManager(plugins_dir)

        # Load and enable all plugins
        for i in range(3):
            manager.load_plugin(f"plugin{i}")
            manager.enable_plugin(f"plugin{i}")

        # All should be enabled
        assert len(manager.get_enabled_plugins()) == 3

        # Shutdown all
        manager.shutdown_all_plugins()

        # None should be enabled
        assert len(manager.get_enabled_plugins()) == 0


class TestGlobalPluginManager:
    """Tests for global plugin manager instance."""

    def test_get_plugin_manager_singleton(self, tmp_path):
        """Test that get_plugin_manager returns singleton."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # First call with plugins_dir
        manager1 = get_plugin_manager(plugins_dir)

        # Second call without plugins_dir
        manager2 = get_plugin_manager()

        # Should be same instance
        assert manager1 is manager2

    def test_get_plugin_manager_uses_first_plugins_dir(self, tmp_path):
        """Test that subsequent calls use first plugins_dir."""
        dir1 = tmp_path / "plugins1"
        dir2 = tmp_path / "plugins2"
        dir1.mkdir()
        dir2.mkdir()

        manager1 = get_plugin_manager(dir1)
        manager2 = get_plugin_manager(dir2)

        # Should be same instance with dir1
        assert manager1 is manager2
        assert manager1.plugins_dir == dir1
