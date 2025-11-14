"""
Template library module for OctoMaster Pro.

Provides workflow templates, template management, and marketplace integration.
"""

from src.templates.manager import TemplateManager, Template
from src.templates.registry import TemplateRegistry
from src.templates.marketplace import TemplateMarketplace

__all__ = [
    "TemplateManager",
    "Template",
    "TemplateRegistry",
    "TemplateMarketplace",
]
