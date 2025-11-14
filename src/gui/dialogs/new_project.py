"""
New project dialog for OctoMaster Pro.

Dialog for creating new projects with templates.
"""

from typing import Optional
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QTextEdit,
    QDialogButtonBox,
    QGroupBox,
    QWidget,
)


class NewProjectDialog(QDialog):
    """Dialog for creating new projects."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize new project dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._project_name = ""
        self._project_path = ""
        self._template = "blank"

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Project name
        name_group = QGroupBox("Project Name")
        name_layout = QVBoxLayout(name_group)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Enter project name...")
        self._name_edit.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self._name_edit)

        layout.addWidget(name_group)

        # Project location
        location_group = QGroupBox("Project Location")
        location_layout = QVBoxLayout(location_group)

        path_layout = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Select project location...")
        self._path_edit.setReadOnly(True)
        path_layout.addWidget(self._path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_location)
        path_layout.addWidget(browse_btn)

        location_layout.addLayout(path_layout)
        layout.addWidget(location_group)

        # Template selection
        template_group = QGroupBox("Project Template")
        template_layout = QVBoxLayout(template_group)

        self._template_combo = QComboBox()
        self._template_combo.addItems(
            [
                "Blank Project",
                "Web Scraping Template",
                "Data Processing Template",
                "Form Automation Template",
                "Testing Template",
            ]
        )
        self._template_combo.currentTextChanged.connect(self._on_template_changed)
        template_layout.addWidget(self._template_combo)

        # Template description
        self._template_desc = QTextEdit()
        self._template_desc.setReadOnly(True)
        self._template_desc.setMaximumHeight(80)
        self._template_desc.setPlainText(
            "Start with an empty project. Build your workflow from scratch."
        )
        template_layout.addWidget(self._template_desc)

        layout.addWidget(template_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)

        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_button.setEnabled(False)

        layout.addWidget(button_box)

        # Set default path
        self._path_edit.setText(str(Path.home() / "OctoMasterProjects"))

    def _on_name_changed(self, text: str) -> None:
        """Handle project name change.

        Args:
            text: New project name
        """
        self._project_name = text.strip()
        self._ok_button.setEnabled(bool(self._project_name))

    def _browse_location(self) -> None:
        """Browse for project location."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Project Location", str(Path.home())
        )

        if directory:
            self._path_edit.setText(directory)
            self._project_path = directory

    def _on_template_changed(self, template: str) -> None:
        """Handle template selection change.

        Args:
            template: Selected template name
        """
        descriptions = {
            "Blank Project": "Start with an empty project. Build your workflow from scratch.",
            "Web Scraping Template": "Pre-configured project for web scraping tasks with common blocks.",
            "Data Processing Template": "Template for data processing workflows with Excel, CSV, and database blocks.",
            "Form Automation Template": "Template for filling and submitting web forms automatically.",
            "Testing Template": "Template for automated testing workflows.",
        }

        self._template_desc.setPlainText(
            descriptions.get(template, "No description available.")
        )

        # Map template names to internal IDs
        template_map = {
            "Blank Project": "blank",
            "Web Scraping Template": "web_scraping",
            "Data Processing Template": "data_processing",
            "Form Automation Template": "form_automation",
            "Testing Template": "testing",
        }

        self._template = template_map.get(template, "blank")

    def _accept(self) -> None:
        """Accept dialog and validate input."""
        if not self._project_name:
            return

        # Get full project path
        base_path = self._path_edit.text() or str(Path.home() / "OctoMasterProjects")
        self._project_path = str(Path(base_path) / self._project_name)

        self.accept()

    def get_project_info(self) -> dict:
        """Get project information.

        Returns:
            Dictionary with project information
        """
        return {
            "name": self._project_name,
            "path": self._project_path,
            "template": self._template,
        }
