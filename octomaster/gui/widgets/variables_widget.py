"""
Variables Widget for OctoMaster Pro.

Displays and manages workflow variables during execution.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QLabel,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from loguru import logger


class AddVariableDialog(QDialog):
    """Dialog for adding/editing variables."""

    def __init__(self, parent=None, variable_name="", variable_value="", variable_type="string"):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Variable")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        # Name
        self.name_edit = QLineEdit(variable_name)
        layout.addRow("Name:", self.name_edit)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "number", "boolean", "list", "dict", "json"])
        self.type_combo.setCurrentText(variable_type)
        layout.addRow("Type:", self.type_combo)

        # Value
        self.value_edit = QTextEdit()
        self.value_edit.setPlainText(str(variable_value))
        self.value_edit.setMaximumHeight(100)
        layout.addRow("Value:", self.value_edit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        """Get variable data."""
        return {
            "name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "value": self.value_edit.toPlainText()
        }


class VariablesWidget(QWidget):
    """Widget for managing workflow variables."""

    variable_changed = pyqtSignal(str, object)  # name, value
    variable_added = pyqtSignal(str, object)
    variable_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar
        toolbar = QHBoxLayout()

        # Search
        toolbar.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter variables...")
        self.search_edit.textChanged.connect(self.filter_variables)
        toolbar.addWidget(self.search_edit)

        toolbar.addStretch()

        # Add button
        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self.add_variable)
        toolbar.addWidget(add_btn)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_variable)
        toolbar.addWidget(edit_btn)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_variable)
        toolbar.addWidget(remove_btn)

        # Clear all button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        toolbar.addWidget(clear_btn)

        layout.addLayout(toolbar)

        # Variables table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_variable)
        layout.addWidget(self.table)

    def set_variable(self, name: str, value: object, var_type: str = None):
        """
        Set a variable value.

        Args:
            name: Variable name
            value: Variable value
            var_type: Variable type (auto-detected if None)
        """
        if var_type is None:
            # Auto-detect type
            if isinstance(value, bool):
                var_type = "boolean"
            elif isinstance(value, (int, float)):
                var_type = "number"
            elif isinstance(value, list):
                var_type = "list"
            elif isinstance(value, dict):
                var_type = "dict"
            else:
                var_type = "string"

        self.variables[name] = {
            "value": value,
            "type": var_type
        }

        self.refresh_table()
        self.variable_changed.emit(name, value)
        logger.debug(f"Variable set: {name} = {value} ({var_type})")

    def get_variable(self, name: str, default=None):
        """Get a variable value."""
        if name in self.variables:
            return self.variables[name]["value"]
        return default

    def has_variable(self, name: str) -> bool:
        """Check if variable exists."""
        return name in self.variables

    def remove_variable_by_name(self, name: str):
        """Remove a variable by name."""
        if name in self.variables:
            del self.variables[name]
            self.refresh_table()
            self.variable_removed.emit(name)
            logger.debug(f"Variable removed: {name}")

    def clear_all(self):
        """Clear all variables."""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear All Variables",
            "Are you sure you want to clear all variables?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.variables.clear()
            self.refresh_table()
            logger.info("All variables cleared")

    def add_variable(self):
        """Show dialog to add a variable."""
        dialog = AddVariableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["name"]:
                self.set_variable(data["name"], data["value"], data["type"])
                self.variable_added.emit(data["name"], data["value"])

    def edit_variable(self):
        """Edit selected variable."""
        row = self.table.currentRow()
        if row >= 0:
            name = self.table.item(row, 0).text()
            var_data = self.variables[name]

            dialog = AddVariableDialog(
                self,
                variable_name=name,
                variable_value=var_data["value"],
                variable_type=var_data["type"]
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data["name"]:
                    # Remove old variable if name changed
                    if data["name"] != name:
                        del self.variables[name]

                    self.set_variable(data["name"], data["value"], data["type"])

    def remove_variable(self):
        """Remove selected variable."""
        row = self.table.currentRow()
        if row >= 0:
            name = self.table.item(row, 0).text()
            self.remove_variable_by_name(name)

    def filter_variables(self, text: str):
        """Filter variables by search text."""
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            value = self.table.item(row, 2).text()

            # Show row if matches search
            matches = (
                text.lower() in name.lower() or
                text.lower() in value.lower()
            )
            self.table.setRowHidden(row, not matches)

    def refresh_table(self):
        """Refresh the variables table."""
        self.table.setRowCount(0)

        for name, var_data in sorted(self.variables.items()):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Name
            name_item = QTableWidgetItem(name)
            self.table.setItem(row, 0, name_item)

            # Type
            type_item = QTableWidgetItem(var_data["type"])
            type_item.setForeground(QColor("#6c757d"))
            self.table.setItem(row, 1, type_item)

            # Value
            value_str = str(var_data["value"])
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            value_item = QTableWidgetItem(value_str)
            self.table.setItem(row, 2, value_item)

    def get_all_variables(self) -> dict:
        """Get all variables as a dictionary."""
        return {name: data["value"] for name, data in self.variables.items()}

    def set_all_variables(self, variables: dict):
        """Set multiple variables at once."""
        for name, value in variables.items():
            self.set_variable(name, value)
