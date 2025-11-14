"""
Visual scraping module for OctoMaster Pro.

Provides intelligent visual scraping with automatic structure detection.
"""

from src.data.scraper.visual_scraper import VisualScraper
from src.data.scraper.table_scraper import TableScraper
from src.data.scraper.list_scraper import ListScraper
from src.data.scraper.pagination import PaginationHandler
from src.data.scraper.anti_bot import AntiBotMeasures

__all__ = [
    "VisualScraper",
    "TableScraper",
    "ListScraper",
    "PaginationHandler",
    "AntiBotMeasures",
]
