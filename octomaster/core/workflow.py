"""
Workflow management for OctoMaster Pro.

A workflow is a collection of connected blocks that define an automation sequence.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime
from loguru import logger

from octomaster.core.block import Block, BlockType


@dataclass
class Connection:
    """Connection between two blocks."""

    id: str = field(default_factory=lambda: str(uuid4()))
    source_block_id: str = ""
    source_output: str = "out"
    target_block_id: str = ""
    target_input: str = "in"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source_block_id,
            "sourceOutput": self.source_output,
            "target": self.target_block_id,
            "targetInput": self.target_input,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Connection":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            source_block_id=data["source"],
            source_output=data.get("sourceOutput", "out"),
            target_block_id=data["target"],
            target_input=data.get("targetInput", "in"),
        )


@dataclass
class Workflow:
    """
    A workflow represents a complete automation sequence.

    It contains blocks and connections between them.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled Workflow"
    description: str = ""
    blocks: List[Block] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)

    # Execution settings
    timeout: int = 60000  # milliseconds
    retry_on_error: bool = False
    max_retries: int = 3

    def add_block(self, block: Block) -> Block:
        """Add a block to the workflow."""
        self.blocks.append(block)
        self.updated_at = datetime.now()
        logger.debug(f"Added block {block.id} to workflow {self.id}")
        return block

    def remove_block(self, block_id: str) -> bool:
        """Remove a block from the workflow."""
        # Remove the block
        self.blocks = [b for b in self.blocks if b.id != block_id]

        # Remove all connections to/from this block
        self.connections = [
            c
            for c in self.connections
            if c.source_block_id != block_id and c.target_block_id != block_id
        ]

        self.updated_at = datetime.now()
        logger.debug(f"Removed block {block_id} from workflow {self.id}")
        return True

    def get_block(self, block_id: str) -> Optional[Block]:
        """Get a block by ID."""
        for block in self.blocks:
            if block.id == block_id:
                return block
        return None

    def connect_blocks(
        self,
        source_id: str,
        target_id: str,
        source_output: str = "out",
        target_input: str = "in",
    ) -> Connection:
        """Connect two blocks."""
        connection = Connection(
            source_block_id=source_id,
            source_output=source_output,
            target_block_id=target_id,
            target_input=target_input,
        )
        self.connections.append(connection)
        self.updated_at = datetime.now()
        logger.debug(f"Connected {source_id} -> {target_id}")
        return connection

    def disconnect_blocks(self, connection_id: str) -> bool:
        """Disconnect two blocks."""
        self.connections = [c for c in self.connections if c.id != connection_id]
        self.updated_at = datetime.now()
        return True

    def get_next_blocks(self, block_id: str) -> List[Block]:
        """Get all blocks connected to the output of the given block."""
        next_block_ids = [
            c.target_block_id for c in self.connections if c.source_block_id == block_id
        ]
        return [b for b in self.blocks if b.id in next_block_ids]

    def get_entry_blocks(self) -> List[Block]:
        """Get all blocks that are entry points (no incoming connections)."""
        blocks_with_inputs = {c.target_block_id for c in self.connections}
        return [b for b in self.blocks if b.id not in blocks_with_inputs]

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the workflow.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check if there are any blocks
        if not self.blocks:
            errors.append("Workflow has no blocks")

        # Check if there are entry points
        entry_blocks = self.get_entry_blocks()
        if not entry_blocks:
            errors.append("Workflow has no entry points")

        # Check for invalid connections
        all_block_ids = {b.id for b in self.blocks}
        for conn in self.connections:
            if conn.source_block_id not in all_block_ids:
                errors.append(f"Connection references non-existent source block {conn.source_block_id}")
            if conn.target_block_id not in all_block_ids:
                errors.append(f"Connection references non-existent target block {conn.target_block_id}")

        # Check for circular dependencies (basic check)
        # TODO: Implement proper cycle detection

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "blocks": [b.to_dict() for b in self.blocks],
            "connections": [c.to_dict() for c in self.connections],
            "settings": {
                "timeout": self.timeout,
                "retry_on_error": self.retry_on_error,
                "max_retries": self.max_retries,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary."""
        blocks = [Block.from_dict(b) for b in data.get("blocks", [])]
        connections = [Connection.from_dict(c) for c in data.get("connections", [])]
        settings = data.get("settings", {})

        return cls(
            id=data.get("id", str(uuid4())),
            name=data.get("name", "Untitled Workflow"),
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            blocks=blocks,
            connections=connections,
            timeout=settings.get("timeout", 60000),
            retry_on_error=settings.get("retry_on_error", False),
            max_retries=settings.get("max_retries", 3),
        )

    def save(self, file_path: Path) -> None:
        """Save workflow to file."""
        data = self.to_dict()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Workflow saved to {file_path}")

    @classmethod
    def load(cls, file_path: Path) -> "Workflow":
        """Load workflow from file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        workflow = cls.from_dict(data)
        logger.info(f"Workflow loaded from {file_path}")
        return workflow

    def export_to_python(self) -> str:
        """Export workflow as Python code."""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            f"Auto-generated script from workflow: {self.name}",
            f"Description: {self.description}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "from playwright.sync_api import sync_playwright",
            "",
            "",
            "def main():",
            "    with sync_playwright() as p:",
            "        browser = p.chromium.launch(headless=False)",
            "        page = browser.new_page()",
            "",
        ]

        # Generate code for each block
        entry_blocks = self.get_entry_blocks()
        for block in entry_blocks:
            lines.extend(self._block_to_python(block, indent=2))

        lines.extend(
            [
                "",
                "        browser.close()",
                "",
                "",
                'if __name__ == "__main__":',
                "    main()",
            ]
        )

        return "\n".join(lines)

    def _block_to_python(self, block: Block, indent: int = 0) -> List[str]:
        """Convert a block to Python code."""
        prefix = " " * indent
        lines = []

        if block.type == BlockType.OPEN_URL:
            url = block.get_parameter("url", "")
            lines.append(f'{prefix}page.goto("{url}")')

        elif block.type == BlockType.CLICK:
            selector = block.get_parameter("selector", "")
            lines.append(f'{prefix}page.click("{selector}")')

        elif block.type == BlockType.TYPE_TEXT:
            selector = block.get_parameter("selector", "")
            text = block.get_parameter("text", "")
            lines.append(f'{prefix}page.fill("{selector}", "{text}")')

        elif block.type == BlockType.WAIT_TIME:
            duration = block.get_parameter("duration", 1000)
            lines.append(f"{prefix}page.wait_for_timeout({duration})")

        elif block.type == BlockType.SCREENSHOT:
            path = block.get_parameter("path", "screenshot.png")
            lines.append(f'{prefix}page.screenshot(path="{path}")')

        # Add more block types...
        lines.append("")

        # Process next blocks
        next_blocks = self.get_next_blocks(block.id)
        for next_block in next_blocks:
            lines.extend(self._block_to_python(next_block, indent))

        return lines

    def __repr__(self) -> str:
        return f"Workflow(id={self.id[:8]}, name={self.name}, blocks={len(self.blocks)})"
