"""
Data storage module for OctoMaster Pro.

Provides universal data storage with support for multiple formats:
JSON, CSV, Excel, SQLite, PostgreSQL, MySQL.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import csv
from datetime import datetime
from loguru import logger

from src.data.types import StorageType, ExtractedData


class DataStorage:
    """Universal data storage with multiple format support."""

    def __init__(
        self,
        storage_type: StorageType = StorageType.JSON,
        path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> None:
        """Initialize storage.

        Args:
            storage_type: Type of storage (json, csv, excel, sqlite, postgres)
            path: Path to storage file/database
            **kwargs: Additional storage-specific options
        """
        self.storage_type = storage_type
        self.path = Path(path) if path else Path(f"data.{storage_type.value}")
        self.data: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "created": datetime.now().isoformat(),
            "storage_type": storage_type.value,
        }
        self.options = kwargs

        logger.info(f"Initialized {storage_type.value} storage: {self.path}")

    def add_row(self, row: Dict[str, Any]) -> None:
        """Add single row to storage.

        Args:
            row: Data row as dictionary
        """
        self.data.append(row)
        logger.debug(f"Added row: {len(self.data)} total rows")

    def add_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Add multiple rows to storage.

        Args:
            rows: List of data rows
        """
        self.data.extend(rows)
        logger.info(f"Added {len(rows)} rows: {len(self.data)} total")

    def save(self) -> bool:
        """Save data to file.

        Returns:
            True if successful
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            if self.storage_type == StorageType.JSON:
                self._save_json()
            elif self.storage_type == StorageType.CSV:
                self._save_csv()
            elif self.storage_type == StorageType.EXCEL:
                self._save_excel()
            elif self.storage_type == StorageType.SQLITE:
                self._save_sqlite()
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")

            logger.info(f"Saved {len(self.data)} rows to {self.path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False

    def load(self) -> List[Dict[str, Any]]:
        """Load data from file.

        Returns:
            Loaded data rows
        """
        try:
            if not self.path.exists():
                logger.warning(f"File not found: {self.path}")
                return []

            if self.storage_type == StorageType.JSON:
                data = self._load_json()
            elif self.storage_type == StorageType.CSV:
                data = self._load_csv()
            elif self.storage_type == StorageType.EXCEL:
                data = self._load_excel()
            elif self.storage_type == StorageType.SQLITE:
                data = self._load_sqlite()
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")

            self.data = data
            logger.info(f"Loaded {len(data)} rows from {self.path}")
            return data

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return []

    def clear(self) -> None:
        """Clear all data."""
        self.data.clear()
        logger.debug("Cleared storage data")

    def get_row_count(self) -> int:
        """Get number of rows.

        Returns:
            Row count
        """
        return len(self.data)

    def _save_json(self) -> None:
        """Save as JSON."""
        output = {
            "metadata": self.metadata,
            "data": self.data,
            "row_count": len(self.data),
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    def _load_json(self) -> List[Dict[str, Any]]:
        """Load from JSON.

        Returns:
            Loaded data
        """
        with open(self.path, "r", encoding="utf-8") as f:
            content = json.load(f)

        # Handle both formats: with metadata and without
        if isinstance(content, dict) and "data" in content:
            self.metadata = content.get("metadata", {})
            return content["data"]
        elif isinstance(content, list):
            return content
        else:
            return []

    def _save_csv(self) -> None:
        """Save as CSV."""
        if not self.data:
            logger.warning("No data to save")
            return

        # Get all unique keys from all rows
        fieldnames = set()
        for row in self.data:
            fieldnames.update(row.keys())

        fieldnames = sorted(fieldnames)

        with open(self.path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)

    def _load_csv(self) -> List[Dict[str, Any]]:
        """Load from CSV.

        Returns:
            Loaded data
        """
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _save_excel(self) -> None:
        """Save as Excel."""
        try:
            import pandas as pd

            if not self.data:
                logger.warning("No data to save")
                return

            df = pd.DataFrame(self.data)

            # Write to Excel
            sheet_name = self.options.get("sheet_name", "Sheet1")

            with pd.ExcelWriter(self.path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Add metadata sheet if requested
                if self.options.get("include_metadata", True):
                    metadata_df = pd.DataFrame([self.metadata])
                    metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

        except ImportError:
            logger.error("pandas and openpyxl required for Excel support")
            raise

    def _load_excel(self) -> List[Dict[str, Any]]:
        """Load from Excel.

        Returns:
            Loaded data
        """
        try:
            import pandas as pd

            sheet_name = self.options.get("sheet_name", 0)  # First sheet by default
            df = pd.read_excel(self.path, sheet_name=sheet_name)

            # Convert DataFrame to list of dicts
            return df.to_dict("records")

        except ImportError:
            logger.error("pandas and openpyxl required for Excel support")
            raise

    def _save_sqlite(self) -> None:
        """Save to SQLite database."""
        try:
            import sqlite3

            if not self.data:
                logger.warning("No data to save")
                return

            # Get table name
            table_name = self.options.get("table_name", "data")

            # Connect to database
            conn = sqlite3.connect(self.path)
            cursor = conn.cursor()

            # Create table if not exists
            if self.data:
                columns = self.data[0].keys()
                column_defs = ", ".join([f"{col} TEXT" for col in columns])
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
                )

                # Insert data
                for row in self.data:
                    placeholders = ", ".join(["?" for _ in row])
                    columns_str = ", ".join(row.keys())
                    values = tuple(str(v) for v in row.values())

                    cursor.execute(
                        f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                        values,
                    )

            conn.commit()
            conn.close()

        except ImportError:
            logger.error("sqlite3 required for SQLite support")
            raise

    def _load_sqlite(self) -> List[Dict[str, Any]]:
        """Load from SQLite database.

        Returns:
            Loaded data
        """
        try:
            import sqlite3

            table_name = self.options.get("table_name", "data")

            conn = sqlite3.connect(self.path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")

            rows = cursor.fetchall()
            data = [dict(row) for row in rows]

            conn.close()

            return data

        except ImportError:
            logger.error("sqlite3 required for SQLite support")
            raise
        except Exception as e:
            logger.error(f"Failed to load from SQLite: {e}")
            return []

    def export_to_format(self, target_format: StorageType, target_path: Path) -> bool:
        """Export data to different format.

        Args:
            target_format: Target storage format
            target_path: Target file path

        Returns:
            True if successful
        """
        try:
            # Create new storage with target format
            target_storage = DataStorage(target_format, target_path, **self.options)

            # Copy data
            target_storage.data = self.data.copy()
            target_storage.metadata = self.metadata.copy()

            # Save
            return target_storage.save()

        except Exception as e:
            logger.error(f"Failed to export to {target_format.value}: {e}")
            return False

    def query(self, filter_func: callable) -> List[Dict[str, Any]]:
        """Query data with filter function.

        Args:
            filter_func: Function that returns True for matching rows

        Returns:
            Filtered rows
        """
        return [row for row in self.data if filter_func(row)]

    def update_row(self, index: int, updates: Dict[str, Any]) -> bool:
        """Update specific row.

        Args:
            index: Row index
            updates: Fields to update

        Returns:
            True if successful
        """
        try:
            if 0 <= index < len(self.data):
                self.data[index].update(updates)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update row: {e}")
            return False

    def delete_row(self, index: int) -> bool:
        """Delete specific row.

        Args:
            index: Row index

        Returns:
            True if successful
        """
        try:
            if 0 <= index < len(self.data):
                del self.data[index]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete row: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Statistics dictionary
        """
        if not self.data:
            return {"row_count": 0, "columns": []}

        # Get all columns
        columns = set()
        for row in self.data:
            columns.update(row.keys())

        return {
            "row_count": len(self.data),
            "columns": sorted(columns),
            "column_count": len(columns),
            "storage_type": self.storage_type.value,
            "file_size": self.path.stat().st_size if self.path.exists() else 0,
        }
