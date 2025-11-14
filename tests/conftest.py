"""
Pytest configuration and fixtures.

This module provides common test fixtures and configuration.
"""

import pytest
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_workflow_path(temp_dir):
    """Provide path to sample workflow file."""
    workflow_file = temp_dir / "test_workflow.json"
    workflow_file.write_text('{"nodes": [], "connections": []}')
    return workflow_file
