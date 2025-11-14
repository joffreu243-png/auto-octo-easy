"""
Core application module for OctoMaster Pro.

This module contains the core application logic, configuration management,
logging setup, event system, and plugin management.
"""

from src.core.exceptions import (
    OctoMasterError,
    ConfigurationError,
    WorkflowError,
    BrowserError,
    PluginError,
)
from src.core.config import Config, get_config
from src.core.logger import setup_logger, get_logger
from src.core.events import EventBus, Event
from src.core.state import AppState
from src.core.app import Application

__all__ = [
    # Exceptions
    "OctoMasterError",
    "ConfigurationError",
    "WorkflowError",
    "BrowserError",
    "PluginError",
    # Configuration
    "Config",
    "get_config",
    # Logging
    "setup_logger",
    "get_logger",
    # Events
    "EventBus",
    "Event",
    # State
    "AppState",
    # Application
    "Application",
]
