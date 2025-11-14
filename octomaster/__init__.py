"""
OctoMaster Pro - Revolutionary Browser Automation Platform

A visual workflow builder for browser automation with AI assistance,
action recording, and seamless integration with Octo Browser.
"""

__version__ = "0.1.0-alpha"
__author__ = "OctoMaster Team"
__email__ = "support@octomaster.pro"
__license__ = "MIT"

from octomaster.core import Workflow, Block
from octomaster.automation import Browser, Recorder
from octomaster.ai import AIAssistant

__all__ = [
    "Workflow",
    "Block",
    "Browser",
    "Recorder",
    "AIAssistant",
    "__version__",
]
