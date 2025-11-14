"""
Project Explorer widget.

Shows the project structure, scripts, data files, etc.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger


class ProjectExplorer(QWidget):
    """Project explorer panel."""

    # Signals
    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("<b>Project Explorer</b>")
        layout.addWidget(title)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        layout.addWidget(self.search_box)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree)

        # Populate tree
        self.populate_tree()

    def populate_tree(self):
        """Populate the project tree."""
        # Scripts
        scripts_item = QTreeWidgetItem(self.tree, ["📁 Scripts"])
        scripts_item.setExpanded(True)

        # Data
        data_item = QTreeWidgetItem(self.tree, ["📁 Data"])

        # Logs
        logs_item = QTreeWidgetItem(self.tree, ["📁 Logs"])

        # Settings
        settings_item = QTreeWidgetItem(self.tree, ["⚙️ Settings"])

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        text = item.text(column)
        logger.debug(f"Item clicked: {text}")
        self.file_selected.emit(text)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click."""
        text = item.text(column)
        logger.debug(f"Item double-clicked: {text}")
        self.file_double_clicked.emit(text)
