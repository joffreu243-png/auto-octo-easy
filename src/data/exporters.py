"""
Data exporters for different formats.
"""

from typing import List, Dict, Any
from pathlib import Path
import json
import csv
from loguru import logger

from src.data.types import StorageType, ExportConfig


class DataExporter:
    """Export data to various formats."""

    @staticmethod
    def export(data: List[Dict[str, Any]], config: ExportConfig) -> bool:
        """Export data using configuration.

        Args:
            data: Data to export
            config: Export configuration

        Returns:
            True if successful
        """
        try:
            config.output_path.parent.mkdir(parents=True, exist_ok=True)

            if config.format == StorageType.JSON:
                return DataExporter.export_json(data, config.output_path, config)
            elif config.format == StorageType.CSV:
                return DataExporter.export_csv(data, config.output_path, config)
            elif config.format == StorageType.EXCEL:
                return DataExporter.export_excel(data, config.output_path, config)
            else:
                logger.error(f"Unsupported format: {config.format}")
                return False

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    @staticmethod
    def export_json(data: List[Dict[str, Any]], path: Path, config: ExportConfig) -> bool:
        """Export to JSON.

        Args:
            data: Data to export
            path: Output path
            config: Export config

        Returns:
            True if successful
        """
        try:
            indent = 2 if config.pretty_print else None

            with open(path, 'w', encoding=config.encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            logger.info(f"Exported {len(data)} rows to JSON: {path}")
            return True

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False

    @staticmethod
    def export_csv(data: List[Dict[str, Any]], path: Path, config: ExportConfig) -> bool:
        """Export to CSV.

        Args:
            data: Data to export
            path: Output path
            config: Export config

        Returns:
            True if successful
        """
        try:
            if not data:
                return False

            fieldnames = list(data[0].keys())

            with open(path, 'w', encoding=config.encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=config.delimiter)
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"Exported {len(data)} rows to CSV: {path}")
            return True

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False

    @staticmethod
    def export_excel(data: List[Dict[str, Any]], path: Path, config: ExportConfig) -> bool:
        """Export to Excel.

        Args:
            data: Data to export
            path: Output path
            config: Export config

        Returns:
            True if successful
        """
        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_excel(path, sheet_name=config.sheet_name, index=False)

            logger.info(f"Exported {len(data)} rows to Excel: {path}")
            return True

        except ImportError:
            logger.error("pandas and openpyxl required for Excel export")
            return False
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return False
