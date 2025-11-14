"""
Type definitions for data module.

Defines data types, models, and enums for data storage and scraping.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path


class StorageType(Enum):
    """Storage format types."""

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class DataType(Enum):
    """Data field types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    JSON = "json"


class StructureType(Enum):
    """Page structure types."""

    LIST = "list"
    TABLE = "table"
    CARDS = "cards"
    FORM = "form"
    SINGLE = "single"


class PaginationType(Enum):
    """Pagination types."""

    BUTTON = "button"
    INFINITE_SCROLL = "infinite_scroll"
    URL_PARAM = "url_param"
    LOAD_MORE = "load_more"


@dataclass
class FieldDefinition:
    """Definition of a data field."""

    name: str
    data_type: DataType = DataType.STRING
    selector: Optional[str] = None
    attribute: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    transform: Optional[str] = None  # Transform function name
    validate: Optional[str] = None  # Validator name


@dataclass
class ExtractedData:
    """Container for extracted data."""

    url: str
    timestamp: datetime
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
            "errors": self.errors,
            "total_records": len(self.data),
        }


@dataclass
class ScrapingConfig:
    """Configuration for scraping session."""

    start_url: str
    structure_type: StructureType
    fields: List[FieldDefinition]
    pagination: Optional[Dict[str, Any]] = None
    max_pages: int = 1
    delay_between_requests: float = 1.0
    timeout: int = 30000
    retry_count: int = 3
    use_stealth: bool = True
    anti_bot: bool = True
    storage_type: StorageType = StorageType.JSON
    storage_path: Optional[Path] = None


@dataclass
class PaginationConfig:
    """Pagination configuration."""

    type: PaginationType
    selector: Optional[str] = None
    url_pattern: Optional[str] = None
    param_name: Optional[str] = None
    max_pages: int = 10
    wait_after_load: float = 2.0


@dataclass
class TableData:
    """Extracted table data."""

    headers: List[str]
    rows: List[List[Any]]
    url: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert to list of dictionaries.

        Returns:
            List of row dictionaries
        """
        return [dict(zip(self.headers, row)) for row in self.rows]


@dataclass
class ListData:
    """Extracted list data."""

    items: List[str]
    url: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field: Optional[str] = None
    value: Optional[Any] = None


@dataclass
class ExportConfig:
    """Configuration for data export."""

    format: StorageType
    output_path: Path
    include_metadata: bool = True
    pretty_print: bool = True
    encoding: str = "utf-8"
    delimiter: str = ","  # For CSV
    sheet_name: str = "Sheet1"  # For Excel


@dataclass
class ScrapingResult:
    """Result of scraping operation."""

    success: bool
    data: Optional[ExtractedData] = None
    error: Optional[str] = None
    pages_scraped: int = 0
    records_extracted: int = 0
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AntiBot Config:
    """Anti-bot configuration."""

    random_user_agent: bool = True
    random_viewport: bool = True
    human_like_delays: bool = True
    min_delay_ms: int = 100
    max_delay_ms: int = 500
    scroll_like_human: bool = True
    solve_captchas: bool = False
    captcha_service: Optional[str] = None
    stealth_mode: bool = True
