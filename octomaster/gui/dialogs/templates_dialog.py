"""
Templates Dialog for OctoMaster Pro.

Dialog for browsing and using workflow templates.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QPushButton,
    QLabel,
    QGroupBox,
    QDialogButtonBox,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger


class TemplatesDialog(QDialog):
    """Dialog for browsing and using workflow templates."""

    template_selected = pyqtSignal(object)  # Emits selected template

    def __init__(self, template_manager=None, parent=None):
        """
        Initialize templates dialog.

        Args:
            template_manager: TemplateManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.template_manager = template_manager
        self.selected_template = None
        self.setWindowTitle("Workflow Templates")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._load_templates()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>📚 Workflow Template Library</h2>")
        layout.addWidget(header)

        # Main content - horizontal split
        content_layout = QHBoxLayout()

        # Left: Template list
        left_panel = QGroupBox("Available Templates")
        left_layout = QVBoxLayout(left_panel)

        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        left_layout.addWidget(self.template_list)

        # Filter/search could be added here

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_templates)
        left_layout.addWidget(refresh_btn)

        content_layout.addWidget(left_panel, 1)

        # Right: Template preview
        right_panel = QGroupBox("Template Details")
        right_layout = QVBoxLayout(right_panel)

        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setPlaceholderText("Select a template to view details...")
        right_layout.addWidget(self.template_preview)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.use_btn = QPushButton("✨ Use Template")
        self.use_btn.clicked.connect(self._use_template)
        self.use_btn.setEnabled(False)
        actions_layout.addWidget(self.use_btn)

        self.preview_btn = QPushButton("👁️ Preview Workflow")
        self.preview_btn.clicked.connect(self._preview_template)
        self.preview_btn.setEnabled(False)
        actions_layout.addWidget(self.preview_btn)

        actions_layout.addStretch()

        right_layout.addLayout(actions_layout)

        content_layout.addWidget(right_panel, 2)

        layout.addLayout(content_layout)

        # Bottom buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_templates(self):
        """Load templates from template manager."""
        self.template_list.clear()
        self.template_preview.clear()

        if not self.template_manager:
            item = QListWidgetItem("⚠️ No template manager available")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.template_list.addItem(item)
            return

        try:
            # Get templates from template manager
            templates = getattr(self.template_manager, 'templates', [])

            if not templates:
                item = QListWidgetItem("📦 No templates found")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.template_list.addItem(item)

                # Add info about how to add templates
                info_item = QListWidgetItem("💡 Templates can be found in resources/templates/")
                info_item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.template_list.addItem(info_item)
                return

            # Group templates by category
            categories = {}
            for template in templates:
                category = getattr(template, 'category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(template)

            # Add templates by category
            for category, cat_templates in sorted(categories.items()):
                # Category header
                header = QListWidgetItem(f"📁 {category}")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                header.setBackground(Qt.GlobalColor.lightGray)
                self.template_list.addItem(header)

                # Templates in this category
                for template in cat_templates:
                    name = getattr(template, 'name', 'Unnamed Template')
                    item = QListWidgetItem(f"  📄 {name}")
                    item.setData(Qt.ItemDataRole.UserRole, template)
                    self.template_list.addItem(item)

            logger.info(f"Loaded {len(templates)} templates")

        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            item = QListWidgetItem(f"❌ Error loading templates: {e}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.template_list.addItem(item)

    def _on_template_selected(self, current, previous):
        """Handle template selection."""
        if not current:
            self.template_preview.clear()
            self.use_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            return

        template = current.data(Qt.ItemDataRole.UserRole)
        if not template:
            self.use_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            return

        self.selected_template = template

        # Display template details
        name = getattr(template, 'name', 'Unnamed')
        description = getattr(template, 'description', 'No description')
        category = getattr(template, 'category', 'Other')
        author = getattr(template, 'author', 'Unknown')

        # Get workflow details
        workflow = getattr(template, 'workflow', None)
        block_count = len(workflow.blocks) if workflow else 0

        # Get required inputs
        inputs = getattr(template, 'inputs', {})
        inputs_html = ""
        if inputs:
            inputs_html = "<p><b>Required Inputs:</b></p><ul>"
            for input_name, input_desc in inputs.items():
                inputs_html += f"<li><code>{input_name}</code>: {input_desc}</li>"
            inputs_html += "</ul>"

        preview_html = f"""
<h3>📄 {name}</h3>
<p><b>Category:</b> {category}</p>
<p><b>Author:</b> {author}</p>
<p><b>Blocks:</b> {block_count}</p>
<hr>
<p><b>Description:</b></p>
<p>{description}</p>
{inputs_html}
        """.strip()

        self.template_preview.setHtml(preview_html)

        # Enable buttons
        self.use_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)

    def _use_template(self):
        """Use the selected template to create a new workflow."""
        if not self.selected_template:
            return

        try:
            # Get required inputs from user
            inputs = getattr(self.selected_template, 'inputs', {})
            input_values = {}

            if inputs:
                for input_name, input_desc in inputs.items():
                    value, ok = QInputDialog.getText(
                        self,
                        "Template Input",
                        f"{input_desc}\n\nEnter value for '{input_name}':",
                    )
                    if not ok:
                        return  # User cancelled
                    input_values[input_name] = value

            # Create workflow from template
            if hasattr(self.selected_template, 'create_workflow'):
                workflow = self.selected_template.create_workflow(input_values)
                logger.info(f"Created workflow from template: {self.selected_template.name}")

                # Emit signal with workflow
                self.template_selected.emit(workflow)

                QMessageBox.information(
                    self,
                    "Success",
                    f"Workflow created from template '{self.selected_template.name}'"
                )
                self.accept()
            else:
                logger.warning("Template does not have create_workflow method")
                QMessageBox.warning(
                    self,
                    "Not Implemented",
                    "This template cannot be used yet"
                )

        except Exception as e:
            logger.error(f"Failed to use template: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create workflow from template:\n{e}"
            )

    def _preview_template(self):
        """Preview the template workflow."""
        if not self.selected_template:
            return

        # Get workflow from template
        workflow = getattr(self.selected_template, 'workflow', None)
        if not workflow:
            QMessageBox.information(
                self,
                "Preview",
                "No workflow preview available for this template"
            )
            return

        # Show workflow details
        blocks = getattr(workflow, 'blocks', [])
        connections = getattr(workflow, 'connections', [])

        preview_text = f"Workflow: {workflow.name}\n\n"
        preview_text += f"Blocks ({len(blocks)}):\n"
        for i, block in enumerate(blocks, 1):
            preview_text += f"  {i}. {block.name} ({block.type.value})\n"

        preview_text += f"\nConnections ({len(connections)}):\n"
        for conn in connections:
            preview_text += f"  • {conn.source_block_id} → {conn.target_block_id}\n"

        QMessageBox.information(self, "Template Preview", preview_text)

    def get_selected_template(self):
        """Get the selected template."""
        return self.selected_template
