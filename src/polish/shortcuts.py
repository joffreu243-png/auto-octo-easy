"""
Keyboard shortcuts for OctoMaster Pro.

Global keyboard shortcuts for common actions.
"""

from typing import Dict, Callable, List
from loguru import logger


class KeyboardShortcuts:
    """Keyboard shortcuts manager."""

    def __init__(self):
        """Initialize shortcuts."""
        self.shortcuts: Dict[str, Dict[str, any]] = {}
        self._setup_default_shortcuts()
        logger.info("KeyboardShortcuts initialized")

    def _setup_default_shortcuts(self) -> None:
        """Setup default shortcuts."""
        self.shortcuts = {
            # File operations
            "Ctrl+N": {"action": "new_workflow", "description": "New workflow"},
            "Ctrl+O": {"action": "open_workflow", "description": "Open workflow"},
            "Ctrl+S": {"action": "save_workflow", "description": "Save workflow"},
            "Ctrl+Shift+S": {"action": "save_as", "description": "Save workflow as..."},

            # Edit operations
            "Ctrl+Z": {"action": "undo", "description": "Undo"},
            "Ctrl+Y": {"action": "redo", "description": "Redo"},
            "Ctrl+C": {"action": "copy", "description": "Copy"},
            "Ctrl+V": {"action": "paste", "description": "Paste"},
            "Delete": {"action": "delete", "description": "Delete selected"},

            # Execution
            "F5": {"action": "run_workflow", "description": "Run workflow"},
            "Shift+F5": {"action": "stop_workflow", "description": "Stop workflow"},
            "Ctrl+R": {"action": "start_recording", "description": "Start recording"},
            "Ctrl+Shift+R": {"action": "stop_recording", "description": "Stop recording"},

            # View
            "F11": {"action": "fullscreen", "description": "Toggle fullscreen"},
            "Ctrl++": {"action": "zoom_in", "description": "Zoom in"},
            "Ctrl+-": {"action": "zoom_out", "description": "Zoom out"},
            "Ctrl+0": {"action": "zoom_reset", "description": "Reset zoom"},

            # Navigation
            "Ctrl+1": {"action": "show_dashboard", "description": "Show dashboard"},
            "Ctrl+2": {"action": "show_recorder", "description": "Show recorder"},
            "Ctrl+3": {"action": "show_editor", "description": "Show node editor"},
            "Ctrl+4": {"action": "show_scheduler", "description": "Show scheduler"},

            # Help
            "F1": {"action": "show_help", "description": "Show help"},
            "Ctrl+Shift+P": {"action": "command_palette", "description": "Command palette"},
        }

    def register_shortcut(self, keys: str, action: str, description: str) -> None:
        """Register custom shortcut.

        Args:
            keys: Key combination (e.g., "Ctrl+K")
            action: Action name
            description: Description
        """
        self.shortcuts[keys] = {"action": action, "description": description}
        logger.debug(f"Registered shortcut: {keys} -> {action}")

    def get_shortcut(self, keys: str) -> str:
        """Get action for key combination.

        Args:
            keys: Key combination

        Returns:
            Action name or empty string
        """
        shortcut = self.shortcuts.get(keys)
        return shortcut["action"] if shortcut else ""

    def get_all_shortcuts(self) -> List[Dict[str, str]]:
        """Get all shortcuts.

        Returns:
            List of shortcut dictionaries
        """
        return [
            {"keys": keys, **info}
            for keys, info in self.shortcuts.items()
        ]

    def get_shortcuts_by_category(self) -> Dict[str, List[Dict[str, str]]]:
        """Get shortcuts grouped by category.

        Returns:
            Categorized shortcuts
        """
        categories = {
            "File": ["Ctrl+N", "Ctrl+O", "Ctrl+S", "Ctrl+Shift+S"],
            "Edit": ["Ctrl+Z", "Ctrl+Y", "Ctrl+C", "Ctrl+V", "Delete"],
            "Execution": ["F5", "Shift+F5", "Ctrl+R", "Ctrl+Shift+R"],
            "View": ["F11", "Ctrl++", "Ctrl+-", "Ctrl+0"],
            "Navigation": ["Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4"],
            "Help": ["F1", "Ctrl+Shift+P"],
        }

        result = {}
        for category, keys_list in categories.items():
            result[category] = [
                {"keys": keys, **self.shortcuts[keys]}
                for keys in keys_list
                if keys in self.shortcuts
            ]

        return result
