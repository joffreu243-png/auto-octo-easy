"""
Data parsers for different formats.
"""

import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger


class JSONParser:
    """Parse JSON data."""

    @staticmethod
    def parse(content: str) -> Any:
        """Parse JSON string.

        Args:
            content: JSON string

        Returns:
            Parsed data
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None

    @staticmethod
    def parse_file(file_path: Path) -> Any:
        """Parse JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse JSON file: {e}")
            return None


class CSVParser:
    """Parse CSV data."""

    @staticmethod
    def parse(content: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """Parse CSV string.

        Args:
            content: CSV string
            delimiter: CSV delimiter

        Returns:
            List of row dictionaries
        """
        try:
            import io
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            return list(reader)
        except Exception as e:
            logger.error(f"CSV parse error: {e}")
            return []

    @staticmethod
    def parse_file(file_path: Path, delimiter: str = ',') -> List[Dict[str, Any]]:
        """Parse CSV file.

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter

        Returns:
            List of row dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            return []


class XMLParser:
    """Parse XML data."""

    @staticmethod
    def parse(content: str) -> Any:
        """Parse XML string.

        Args:
            content: XML string

        Returns:
            Parsed XML tree
        """
        try:
            import xml.etree.ElementTree as ET
            return ET.fromstring(content)
        except Exception as e:
            logger.error(f"XML parse error: {e}")
            return None

    @staticmethod
    def parse_file(file_path: Path) -> Any:
        """Parse XML file.

        Args:
            file_path: Path to XML file

        Returns:
            Parsed XML tree
        """
        try:
            import xml.etree.ElementTree as ET
            return ET.parse(file_path).getroot()
        except Exception as e:
            logger.error(f"Failed to parse XML file: {e}")
            return None
