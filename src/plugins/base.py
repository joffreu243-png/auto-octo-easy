"""
Base plugin classes for OctoMaster Pro.

Defines base plugin architecture and plugin types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from loguru import logger


class PluginBase(ABC):
    """Base class for all plugins."""

    # Plugin metadata
    name: str = "Unknown Plugin"
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = ""
    website: Optional[str] = None
    license: str = "MIT"

    # Dependencies
    requires: List[str] = []  # Required plugins
    conflicts: List[str] = []  # Conflicting plugins

    def __init__(self, app: Any = None):
        """Initialize plugin.

        Args:
            app: Main OctoMasterApp instance
        """
        self.app = app
        self.enabled = False
        self.config: Dict[str, Any] = {}

        logger.debug(f"Plugin initialized: {self.name}")

    @abstractmethod
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass

    @abstractmethod
    def on_enable(self) -> None:
        """Called when plugin is enabled."""
        pass

    @abstractmethod
    def on_disable(self) -> None:
        """Called when plugin is disabled."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set plugin configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    # Helper methods for plugin capabilities

    def register_block(self, block_class: type) -> None:
        """Register custom block type.

        Args:
            block_class: Block class to register
        """
        if self.app and hasattr(self.app, "nodes"):
            self.app.nodes.register_block(block_class)
            logger.info(f"Registered block: {block_class.__name__}")

    def register_menu_item(self, menu_path: str, callback: callable) -> None:
        """Add menu item to GUI.

        Args:
            menu_path: Menu path (e.g., "Tools/My Plugin")
            callback: Callback function
        """
        if self.app and hasattr(self.app, "gui"):
            self.app.gui.add_menu_item(menu_path, callback)
            logger.info(f"Registered menu item: {menu_path}")

    def register_toolbar_button(
        self, icon: str, tooltip: str, callback: callable
    ) -> None:
        """Add button to toolbar.

        Args:
            icon: Icon path or name
            tooltip: Tooltip text
            callback: Callback function
        """
        if self.app and hasattr(self.app, "gui"):
            self.app.gui.add_toolbar_button(icon, tooltip, callback)
            logger.info(f"Registered toolbar button: {tooltip}")

    def register_integration(self, name: str, integration_class: type) -> None:
        """Register integration with external service.

        Args:
            name: Integration name
            integration_class: Integration class
        """
        if self.app and hasattr(self.app, "integrations"):
            self.app.integrations.register(name, integration_class)
            logger.info(f"Registered integration: {name}")

    def register_template(self, template: Any) -> None:
        """Register workflow template.

        Args:
            template: Template instance
        """
        if self.app and hasattr(self.app, "templates"):
            self.app.templates.add_template(template)
            logger.info(f"Registered template: {template.name}")

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information.

        Returns:
            Plugin metadata dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "website": self.website,
            "license": self.license,
            "enabled": self.enabled,
            "requires": self.requires,
            "conflicts": self.conflicts,
        }


class BlockPlugin(PluginBase):
    """Plugin that adds custom workflow blocks."""

    @abstractmethod
    def get_blocks(self) -> List[type]:
        """Return list of block classes.

        Returns:
            List of block classes
        """
        pass

    def on_enable(self) -> None:
        """Register all blocks when enabled."""
        for block_class in self.get_blocks():
            self.register_block(block_class)


class IntegrationPlugin(PluginBase):
    """Plugin that adds integration with external service."""

    @abstractmethod
    def get_integration(self) -> type:
        """Return integration class.

        Returns:
            Integration class
        """
        pass

    @abstractmethod
    def get_integration_name(self) -> str:
        """Return integration name.

        Returns:
            Integration name
        """
        pass

    def on_enable(self) -> None:
        """Register integration when enabled."""
        self.register_integration(self.get_integration_name(), self.get_integration())


class ThemePlugin(PluginBase):
    """Plugin that adds custom theme."""

    @abstractmethod
    def get_stylesheet(self) -> str:
        """Return QSS stylesheet.

        Returns:
            QSS stylesheet string
        """
        pass

    @abstractmethod
    def get_theme_name(self) -> str:
        """Return theme name.

        Returns:
            Theme name
        """
        pass

    def on_enable(self) -> None:
        """Apply theme when enabled."""
        if self.app and hasattr(self.app, "gui"):
            stylesheet = self.get_stylesheet()
            self.app.gui.apply_stylesheet(stylesheet)
            logger.info(f"Applied theme: {self.get_theme_name()}")


class ExporterPlugin(PluginBase):
    """Plugin that adds export format."""

    @abstractmethod
    def export(self, workflow: Any, **options) -> str:
        """Export workflow to format.

        Args:
            workflow: Workflow to export
            **options: Export options

        Returns:
            Exported code/data
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Return format name.

        Returns:
            Format name (e.g., "Python", "JavaScript")
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return file extension.

        Returns:
            File extension (e.g., ".py", ".js")
        """
        pass


class DataSourcePlugin(PluginBase):
    """Plugin that adds data source."""

    @abstractmethod
    async def fetch_data(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch data from source.

        Args:
            params: Fetch parameters

        Returns:
            Fetched data
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Return data source name.

        Returns:
            Source name
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return data schema.

        Returns:
            Schema definition
        """
        pass
