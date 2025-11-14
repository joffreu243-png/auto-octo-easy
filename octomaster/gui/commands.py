"""
Command pattern implementation for Undo/Redo functionality.

Provides undoable commands for workflow editor operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block
from octomaster.core.connection import Connection


class Command(ABC):
    """Base command for undo/redo."""

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def redo(self) -> bool:
        """
        Redo the command.

        Returns:
            True if successful
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get command description."""
        pass


class AddBlockCommand(Command):
    """Command to add a block to workflow."""

    def __init__(self, workflow: Workflow, block: Block, scene=None):
        """
        Initialize command.

        Args:
            workflow: Target workflow
            block: Block to add
            scene: Optional visual editor scene
        """
        self.workflow = workflow
        self.block = block
        self.scene = scene

    def execute(self) -> bool:
        """Execute command."""
        self.workflow.add_block(self.block)
        if self.scene:
            # Add block to visual scene
            from octomaster.gui.widgets.visual_editor import BlockGraphicsItem
            item = BlockGraphicsItem(self.block)
            self.scene.addItem(item)
        return True

    def undo(self) -> bool:
        """Undo command."""
        self.workflow.remove_block(self.block.id)
        if self.scene:
            # Remove block from visual scene
            for item in self.scene.items():
                if hasattr(item, 'block') and item.block.id == self.block.id:
                    self.scene.removeItem(item)
                    break
        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    @property
    def description(self) -> str:
        """Get command description."""
        return f"Add {self.block.name}"


class RemoveBlockCommand(Command):
    """Command to remove a block from workflow."""

    def __init__(self, workflow: Workflow, block_id: str, scene=None):
        """
        Initialize command.

        Args:
            workflow: Target workflow
            block_id: ID of block to remove
            scene: Optional visual editor scene
        """
        self.workflow = workflow
        self.block_id = block_id
        self.scene = scene

        # Store block data for undo
        self.block = workflow.get_block(block_id)
        self.connections = []

        # Store connections involving this block
        for conn in workflow.connections:
            if conn.source_id == block_id or conn.target_id == block_id:
                self.connections.append(conn)

    def execute(self) -> bool:
        """Execute command."""
        # Remove connections first
        for conn in self.connections:
            self.workflow.disconnect_blocks(conn.source_id, conn.target_id)

        # Remove block
        self.workflow.remove_block(self.block_id)

        if self.scene:
            # Remove from visual scene
            for item in self.scene.items():
                if hasattr(item, 'block') and item.block.id == self.block_id:
                    self.scene.removeItem(item)
                    break
        return True

    def undo(self) -> bool:
        """Undo command."""
        # Restore block
        self.workflow.add_block(self.block)

        # Restore connections
        for conn in self.connections:
            self.workflow.connect_blocks(conn.source_id, conn.target_id)

        if self.scene:
            # Restore to visual scene
            from octomaster.gui.widgets.visual_editor import BlockGraphicsItem
            item = BlockGraphicsItem(self.block)
            self.scene.addItem(item)

        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    @property
    def description(self) -> str:
        """Get command description."""
        return f"Remove {self.block.name if self.block else 'block'}"


class MoveBlockCommand(Command):
    """Command to move a block."""

    def __init__(self, block: Block, old_pos: tuple, new_pos: tuple, scene=None):
        """
        Initialize command.

        Args:
            block: Block to move
            old_pos: Old position (x, y)
            new_pos: New position (x, y)
            scene: Optional visual editor scene
        """
        self.block = block
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.scene = scene

    def execute(self) -> bool:
        """Execute command."""
        self.block.position = self.new_pos
        if self.scene:
            self._update_visual_position(self.new_pos)
        return True

    def undo(self) -> bool:
        """Undo command."""
        self.block.position = self.old_pos
        if self.scene:
            self._update_visual_position(self.old_pos)
        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    def _update_visual_position(self, pos: tuple):
        """Update visual position of block."""
        if self.scene:
            for item in self.scene.items():
                if hasattr(item, 'block') and item.block.id == self.block.id:
                    item.setPos(pos[0], pos[1])
                    break

    @property
    def description(self) -> str:
        """Get command description."""
        return f"Move {self.block.name}"


class EditBlockParametersCommand(Command):
    """Command to edit block parameters."""

    def __init__(self, block: Block, old_params: Dict[str, Any], new_params: Dict[str, Any]):
        """
        Initialize command.

        Args:
            block: Block to edit
            old_params: Old parameters
            new_params: New parameters
        """
        self.block = block
        self.old_params = old_params.copy()
        self.new_params = new_params.copy()

    def execute(self) -> bool:
        """Execute command."""
        self.block.parameters = self.new_params.copy()
        return True

    def undo(self) -> bool:
        """Undo command."""
        self.block.parameters = self.old_params.copy()
        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    @property
    def description(self) -> str:
        """Get command description."""
        return f"Edit {self.block.name}"


class ConnectBlocksCommand(Command):
    """Command to connect two blocks."""

    def __init__(self, workflow: Workflow, source_id: str, target_id: str, scene=None):
        """
        Initialize command.

        Args:
            workflow: Target workflow
            source_id: Source block ID
            target_id: Target block ID
            scene: Optional visual editor scene
        """
        self.workflow = workflow
        self.source_id = source_id
        self.target_id = target_id
        self.scene = scene

    def execute(self) -> bool:
        """Execute command."""
        self.workflow.connect_blocks(self.source_id, self.target_id)

        if self.scene:
            # Add connection to visual scene
            source_block = self.workflow.get_block(self.source_id)
            target_block = self.workflow.get_block(self.target_id)
            if source_block and target_block:
                self.scene.add_connection_to_scene(source_block, target_block)

        return True

    def undo(self) -> bool:
        """Undo command."""
        self.workflow.disconnect_blocks(self.source_id, self.target_id)

        if self.scene:
            # Remove connection from visual scene
            # This would need to be implemented in the scene
            pass

        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    @property
    def description(self) -> str:
        """Get command description."""
        return "Connect blocks"


class DisconnectBlocksCommand(Command):
    """Command to disconnect two blocks."""

    def __init__(self, workflow: Workflow, source_id: str, target_id: str, scene=None):
        """
        Initialize command.

        Args:
            workflow: Target workflow
            source_id: Source block ID
            target_id: Target block ID
            scene: Optional visual editor scene
        """
        self.workflow = workflow
        self.source_id = source_id
        self.target_id = target_id
        self.scene = scene

    def execute(self) -> bool:
        """Execute command."""
        self.workflow.disconnect_blocks(self.source_id, self.target_id)

        if self.scene:
            # Remove connection from visual scene
            pass

        return True

    def undo(self) -> bool:
        """Undo command."""
        self.workflow.connect_blocks(self.source_id, self.target_id)

        if self.scene:
            # Add connection to visual scene
            source_block = self.workflow.get_block(self.source_id)
            target_block = self.workflow.get_block(self.target_id)
            if source_block and target_block:
                self.scene.add_connection_to_scene(source_block, target_block)

        return True

    def redo(self) -> bool:
        """Redo command."""
        return self.execute()

    @property
    def description(self) -> str:
        """Get command description."""
        return "Disconnect blocks"


class CommandHistory:
    """Manages command history for undo/redo."""

    def __init__(self, max_history: int = 100):
        """
        Initialize command history.

        Args:
            max_history: Maximum number of commands to keep
        """
        self.max_history = max_history
        self.commands: list[Command] = []
        self.current_index = -1

    def execute(self, command: Command) -> bool:
        """
        Execute a command and add to history.

        Args:
            command: Command to execute

        Returns:
            True if successful
        """
        # Execute command
        if not command.execute():
            return False

        # Remove any commands after current index (they were undone)
        self.commands = self.commands[: self.current_index + 1]

        # Add new command
        self.commands.append(command)
        self.current_index += 1

        # Limit history size
        if len(self.commands) > self.max_history:
            removed_count = len(self.commands) - self.max_history
            self.commands = self.commands[removed_count:]
            self.current_index -= removed_count

        return True

    def undo(self) -> bool:
        """
        Undo last command.

        Returns:
            True if successful
        """
        if not self.can_undo():
            return False

        command = self.commands[self.current_index]
        if command.undo():
            self.current_index -= 1
            return True

        return False

    def redo(self) -> bool:
        """
        Redo next command.

        Returns:
            True if successful
        """
        if not self.can_redo():
            return False

        self.current_index += 1
        command = self.commands[self.current_index]

        if command.redo():
            return True

        self.current_index -= 1
        return False

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_index < len(self.commands) - 1

    def get_undo_description(self) -> Optional[str]:
        """Get description of command to undo."""
        if self.can_undo():
            return self.commands[self.current_index].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of command to redo."""
        if self.can_redo():
            return self.commands[self.current_index + 1].description
        return None

    def clear(self):
        """Clear command history."""
        self.commands.clear()
        self.current_index = -1

    def get_history(self) -> list[str]:
        """
        Get list of command descriptions in history.

        Returns:
            List of command descriptions
        """
        return [cmd.description for cmd in self.commands]
