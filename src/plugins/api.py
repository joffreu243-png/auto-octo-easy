"""
Plugin API for OctoMaster Pro.

Provides API for plugin interaction with application.
"""

from typing import Any, Dict, List, Optional, Callable
from loguru import logger


class PluginAPI:
    """API for plugins to interact with application."""

    def __init__(self, app: Any):
        """Initialize plugin API.

        Args:
            app: Application instance
        """
        self.app = app
        self._hooks: Dict[str, List[Callable]] = {}
        logger.info("PluginAPI initialized")

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register hook callback.

        Args:
            hook_name: Hook name
            callback: Callback function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []

        self._hooks[hook_name].append(callback)
        logger.debug(f"Registered hook: {hook_name}")

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger hook callbacks.

        Args:
            hook_name: Hook name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of callback results
        """
        if hook_name not in self._hooks:
            return []

        results = []
        for callback in self._hooks[hook_name]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook callback failed ({hook_name}): {e}")

        return results

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get application config value.

        Args:
            key: Config key
            default: Default value

        Returns:
            Config value
        """
        if hasattr(self.app, "config"):
            return self.app.config.get(key, default)
        return default

    def set_config(self, key: str, value: Any) -> None:
        """Set application config value.

        Args:
            key: Config key
            value: Value to set
        """
        if hasattr(self.app, "config"):
            self.app.config.set(key, value)

    def show_notification(self, title: str, message: str, level: str = "info") -> None:
        """Show notification to user.

        Args:
            title: Notification title
            message: Notification message
            level: Level (info, warning, error)
        """
        if hasattr(self.app, "gui"):
            self.app.gui.show_notification(title, message, level)

    def execute_command(self, command: str, *args, **kwargs) -> Any:
        """Execute application command.

        Args:
            command: Command name
            *args: Command arguments
            **kwargs: Command keyword arguments

        Returns:
            Command result
        """
        if hasattr(self.app, "commands"):
            return self.app.commands.execute(command, *args, **kwargs)
        return None
