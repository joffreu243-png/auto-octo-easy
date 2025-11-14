"""
Example Block Plugin for OctoMaster Pro.

Provides custom block types for API testing.
"""

from typing import List, Dict, Type
from loguru import logger

from octomaster.core.plugins.plugin import BlockPlugin, PluginMetadata
from octomaster.core.block import Block, BlockType


# Custom block types
class APIRequestBlock(Block):
    """Custom block for making HTTP requests."""

    def __init__(self):
        super().__init__(type=BlockType.CUSTOM)
        self.name = "API Request"
        self.category = "API Testing"
        self.description = "Make HTTP request to API endpoint"

        # Define parameters
        self.parameters = {
            "method": "GET",
            "url": "",
            "headers": {},
            "body": "",
            "timeout": 30,
        }


class AssertResponseBlock(Block):
    """Custom block for asserting API response."""

    def __init__(self):
        super().__init__(type=BlockType.CUSTOM)
        self.name = "Assert Response"
        self.category = "API Testing"
        self.description = "Assert API response status and content"

        self.parameters = {
            "expected_status": 200,
            "assert_body_contains": "",
            "assert_header": "",
        }


class ExtractJSONBlock(Block):
    """Custom block for extracting data from JSON response."""

    def __init__(self):
        super().__init__(type=BlockType.CUSTOM)
        self.name = "Extract JSON"
        self.category = "API Testing"
        self.description = "Extract data from JSON response using JSONPath"

        self.parameters = {
            "json_path": "$.data",
            "output_variable": "extracted_data",
        }


class PluginClass(BlockPlugin):
    """Example block plugin implementation."""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.custom_blocks = []

    def initialize(self) -> bool:
        """Initialize plugin."""
        try:
            logger.info(f"Initializing {self.metadata.name}")

            # Register custom block types
            self.custom_blocks = [
                APIRequestBlock,
                AssertResponseBlock,
                ExtractJSONBlock,
            ]

            logger.info(f"Registered {len(self.custom_blocks)} custom block types")
            return True

        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}")
            return False

    def activate(self) -> bool:
        """Activate plugin."""
        try:
            logger.info(f"Activating {self.metadata.name}")

            timeout = self.get_config("default_timeout", 30)
            retry_count = self.get_config("retry_count", 3)

            logger.info(f"Plugin config: timeout={timeout}s, retries={retry_count}")
            return True

        except Exception as e:
            logger.error(f"Plugin activation failed: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate plugin."""
        try:
            logger.info(f"Deactivating {self.metadata.name}")
            return True

        except Exception as e:
            logger.error(f"Plugin deactivation failed: {e}")
            return False

    def cleanup(self):
        """Cleanup plugin resources."""
        logger.info(f"Cleaning up {self.metadata.name}")
        self.custom_blocks.clear()

    def get_block_types(self) -> List[Type[Block]]:
        """Get custom block types."""
        return self.custom_blocks

    def get_block_categories(self) -> Dict[str, List[str]]:
        """Get block categories."""
        return {
            "API Testing": [
                "api_request",
                "assert_response",
                "extract_json",
            ]
        }
