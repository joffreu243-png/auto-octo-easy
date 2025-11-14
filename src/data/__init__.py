"""
Data and scraping module for OctoMaster Pro.

Provides comprehensive data extraction, storage, transformation, and scraping capabilities.
"""

from src.data.storage import DataStorage
from src.data.extractors import (
    TextExtractor,
    AttributeExtractor,
    LinkExtractor,
    ImageExtractor,
    HTMLExtractor,
    TableExtractor,
    ListExtractor,
    MetaExtractor,
)
from src.data.transformers import DataTransformer
from src.data.validators import (
    EmailValidator,
    URLValidator,
    PhoneValidator,
    NumberValidator,
    RequiredValidator,
    LengthValidator,
)
from src.data.parsers import JSONParser, CSVParser, XMLParser
from src.data.exporters import DataExporter
from src.data.types import (
    StorageType,
    DataType,
    StructureType,
    PaginationType,
    FieldDefinition,
    ExtractedData,
    ScrapingConfig,
    ValidationResult,
    ExportConfig,
)

# Scraper submodule
from src.data.scraper import (
    VisualScraper,
    TableScraper,
    ListScraper,
    PaginationHandler,
    AntiBotMeasures,
)

__all__ = [
    # Storage
    "DataStorage",
    # Extractors
    "TextExtractor",
    "AttributeExtractor",
    "LinkExtractor",
    "ImageExtractor",
    "HTMLExtractor",
    "TableExtractor",
    "ListExtractor",
    "MetaExtractor",
    # Transformers
    "DataTransformer",
    # Validators
    "EmailValidator",
    "URLValidator",
    "PhoneValidator",
    "NumberValidator",
    "RequiredValidator",
    "LengthValidator",
    # Parsers & Exporters
    "JSONParser",
    "CSVParser",
    "XMLParser",
    "DataExporter",
    # Types
    "StorageType",
    "DataType",
    "StructureType",
    "PaginationType",
    "FieldDefinition",
    "ExtractedData",
    "ScrapingConfig",
    "ValidationResult",
    "ExportConfig",
    # Scrapers
    "VisualScraper",
    "TableScraper",
    "ListScraper",
    "PaginationHandler",
    "AntiBotMeasures",
]
