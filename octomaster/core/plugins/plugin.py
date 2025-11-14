"""
Base plugin system for OctoMaster Pro.

Allows extending functionality without modifying core code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Type
from enum import Enum
from pathlib import Path

from octomaster.core.block import Block, BlockType


class PluginType(Enum):
    """Plugin types."""

    BLOCK = "block"  # Custom block types
    INTEGRATION = "integration"  # External service integrations
    THEME = "theme"  # UI themes
    TOOL = "tool"  # Utility tools
    EXPORTER = "exporter"  # Export formats


@dataclass
class PluginMetadata:
    """Plugin metadata."""

    id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType

    # Requirements
    min_app_version: str = "0.1.0"
    max_app_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    # Display
    icon: str = "🔌"
    homepage: Optional[str] = None
    documentation: Optional[str] = None

    # Settings
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.plugin_type, str):
            self.plugin_type = PluginType(self.plugin_type)


class Plugin(ABC):
    """Base plugin class."""

    def __init__(self, metadata: PluginMetadata):
        """
        Initialize plugin.

        Args:
            metadata: Plugin metadata
        """
        self.metadata = metadata
        self._initialized = False
        self._active = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin.

        Called once when plugin is loaded.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def activate(self) -> bool:
        """
        Activate plugin.

        Called when plugin is enabled.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Deactivate plugin.

        Called when plugin is disabled.

        Returns:
            True if successful
        """
        pass

    def cleanup(self):
        """
        Cleanup plugin resources.

        Called when plugin is unloaded.
        """
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.metadata.config.get(key, default)

    def set_config(self, key: str, value: Any):
        """Set configuration value."""
        self.metadata.config[key] = value

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    @property
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self._active

    def __repr__(self):
        return f"<Plugin({self.metadata.name} v{self.metadata.version})>"


class BlockPlugin(Plugin):
    """Plugin that provides custom block types."""

    @abstractmethod
    def get_block_types(self) -> List[Type[Block]]:
        """
        Get custom block types provided by this plugin.

        Returns:
            List of Block classes
        """
        pass

    @abstractmethod
    def get_block_categories(self) -> Dict[str, List[str]]:
        """
        Get block categories.

        Returns:
            Dict mapping category names to block type IDs
        """
        pass


class IntegrationPlugin(Plugin):
    """Plugin that provides external service integration."""

    @abstractmethod
    def get_client_class(self) -> Type:
        """
        Get integration client class.

        Returns:
            Client class
        """
        pass

    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema.

        Returns:
            JSON schema for configuration
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test connection to external service.

        Returns:
            True if connection successful
        """
        pass


class ThemePlugin(Plugin):
    """Plugin that provides UI theme."""

    @abstractmethod
    def get_stylesheet(self) -> str:
        """
        Get Qt stylesheet.

        Returns:
            QSS stylesheet string
        """
        pass

    @abstractmethod
    def get_colors(self) -> Dict[str, str]:
        """
        Get theme colors.

        Returns:
            Dict mapping color names to hex values
        """
        pass

    @abstractmethod
    def get_icons(self) -> Dict[str, Path]:
        """
        Get theme icons.

        Returns:
            Dict mapping icon names to file paths
        """
        pass


class ToolPlugin(Plugin):
    """Plugin that provides utility tools."""

    @abstractmethod
    def get_tool_name(self) -> str:
        """Get tool name."""
        pass

    @abstractmethod
    def get_tool_menu_path(self) -> List[str]:
        """
        Get tool menu path.

        Returns:
            List of menu items (e.g., ["Tools", "My Tool"])
        """
        pass

    @abstractmethod
    async def execute_tool(self, context: Dict[str, Any]) -> Any:
        """
        Execute tool.

        Args:
            context: Execution context

        Returns:
            Tool result
        """
        pass


class ExporterPlugin(Plugin):
    """Plugin that provides export formats."""

    @abstractmethod
    def get_format_name(self) -> str:
        """Get format name (e.g., 'python', 'javascript')."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension (e.g., '.py', '.js')."""
        pass

    @abstractmethod
    def export_workflow(self, workflow, output_path: Path) -> bool:
        """
        Export workflow to this format.

        Args:
            workflow: Workflow to export
            output_path: Output file path

        Returns:
            True if successful
        """
        pass
