"""
Inspector Panel widget.

Shows properties of selected blocks and allows editing them.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QScrollArea,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger

from octomaster.core.block import Block


class InspectorPanel(QWidget):
    """Inspector panel for viewing and editing block properties."""

    property_changed = pyqtSignal(str, str, object)  # block_id, property_name, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_block: Block | None = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("<b>Inspector</b>")
        layout.addWidget(title)

        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Placeholder
        placeholder = QLabel("Select a block to view its properties")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: gray;")
        self.content_layout.addWidget(placeholder)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def set_block(self, block: Block):
        """Set the block to inspect."""
        self.current_block = block
        self.refresh()

    def refresh(self):
        """Refresh the inspector with current block data."""
        # Clear current content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.current_block:
            placeholder = QLabel("Select a block to view its properties")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: gray;")
            self.content_layout.addWidget(placeholder)
            return

        block = self.current_block

        # Block info group
        info_group = QGroupBox("Block Information")
        info_layout = QFormLayout()

        # Name
        name_edit = QLineEdit(block.name)
        name_edit.textChanged.connect(lambda text: self.on_property_changed("name", text))
        info_layout.addRow("Name:", name_edit)

        # Type
        type_label = QLabel(block.type.value)
        info_layout.addRow("Type:", type_label)

        # Category
        category_label = QLabel(block.category)
        info_layout.addRow("Category:", category_label)

        # Enabled
        enabled_check = QCheckBox()
        enabled_check.setChecked(block.enabled)
        enabled_check.toggled.connect(lambda checked: self.on_property_changed("enabled", checked))
        info_layout.addRow("Enabled:", enabled_check)

        info_group.setLayout(info_layout)
        self.content_layout.addWidget(info_group)

        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout()

        # Add parameter editors based on block type
        # TODO: Implement dynamic parameter editors

        params_group.setLayout(params_layout)
        self.content_layout.addWidget(params_group)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()

        desc_edit = QTextEdit()
        desc_edit.setPlainText(block.description)
        desc_edit.setMaximumHeight(100)
        desc_edit.textChanged.connect(
            lambda: self.on_property_changed("description", desc_edit.toPlainText())
        )
        desc_layout.addWidget(desc_edit)

        desc_group.setLayout(desc_layout)
        self.content_layout.addWidget(desc_group)

    def on_property_changed(self, property_name: str, value):
        """Handle property change."""
        if self.current_block:
            setattr(self.current_block, property_name, value)
            self.property_changed.emit(self.current_block.id, property_name, value)
            logger.debug(f"Property changed: {property_name} = {value}")
