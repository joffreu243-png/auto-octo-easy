"""
Automation module for OctoMaster Pro.

Handles browser automation using Playwright, Selenium, etc.
"""

from octomaster.automation.browser import Browser
from octomaster.automation.recorder import Recorder

__all__ = ["Browser", "Recorder"]
