"""
Plugins Dialog for OctoMaster Pro.

Dialog for viewing and managing installed plugins.
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
)
from PyQt6.QtCore import Qt
from loguru import logger


class PluginsDialog(QDialog):
    """Dialog for managing plugins."""

    def __init__(self, plugin_manager=None, parent=None):
        """
        Initialize plugins dialog.

        Args:
            plugin_manager: PluginManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setWindowTitle("Plugins")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_plugins()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>Installed Plugins</h2>")
        layout.addWidget(header)

        # Main content - horizontal split
        content_layout = QHBoxLayout()

        # Left: Plugin list
        left_panel = QGroupBox("Available Plugins")
        left_layout = QVBoxLayout(left_panel)

        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self._on_plugin_selected)
        left_layout.addWidget(self.plugin_list)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_plugins)
        left_layout.addWidget(refresh_btn)

        content_layout.addWidget(left_panel, 1)

        # Right: Plugin details
        right_panel = QGroupBox("Plugin Details")
        right_layout = QVBoxLayout(right_panel)

        self.plugin_details = QTextEdit()
        self.plugin_details.setReadOnly(True)
        self.plugin_details.setPlaceholderText("Select a plugin to view details...")
        right_layout.addWidget(self.plugin_details)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.enable_btn = QPushButton("✅ Enable")
        self.enable_btn.clicked.connect(self._enable_plugin)
        self.enable_btn.setEnabled(False)
        actions_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("⏸️ Disable")
        self.disable_btn.clicked.connect(self._disable_plugin)
        self.disable_btn.setEnabled(False)
        actions_layout.addWidget(self.disable_btn)

        actions_layout.addStretch()

        right_layout.addLayout(actions_layout)

        content_layout.addWidget(right_panel, 2)

        layout.addLayout(content_layout)

        # Bottom buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_plugins(self):
        """Load plugins from plugin manager."""
        self.plugin_list.clear()
        self.plugin_details.clear()

        if not self.plugin_manager:
            item = QListWidgetItem("⚠️ No plugin manager available")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.plugin_list.addItem(item)
            return

        try:
            # Get installed plugins from plugin manager
            plugins = getattr(self.plugin_manager, 'plugins', [])

            if not plugins:
                item = QListWidgetItem("📦 No plugins installed")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.plugin_list.addItem(item)
                return

            for plugin in plugins:
                name = getattr(plugin, 'name', 'Unknown Plugin')
                enabled = getattr(plugin, 'enabled', False)
                icon = "✅" if enabled else "⏸️"
                item = QListWidgetItem(f"{icon} {name}")
                item.setData(Qt.ItemDataRole.UserRole, plugin)
                self.plugin_list.addItem(item)

            logger.info(f"Loaded {len(plugins)} plugins")

        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")
            item = QListWidgetItem(f"❌ Error loading plugins: {e}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.plugin_list.addItem(item)

    def _on_plugin_selected(self, current, previous):
        """Handle plugin selection."""
        if not current:
            self.plugin_details.clear()
            self.enable_btn.setEnabled(False)
            self.disable_btn.setEnabled(False)
            return

        plugin = current.data(Qt.ItemDataRole.UserRole)
        if not plugin:
            return

        # Display plugin details
        name = getattr(plugin, 'name', 'Unknown')
        version = getattr(plugin, 'version', 'N/A')
        author = getattr(plugin, 'author', 'Unknown')
        description = getattr(plugin, 'description', 'No description available')
        enabled = getattr(plugin, 'enabled', False)

        details = f"""
<h3>{name}</h3>
<p><b>Version:</b> {version}</p>
<p><b>Author:</b> {author}</p>
<p><b>Status:</b> {'<span style="color: green;">Enabled</span>' if enabled else '<span style="color: gray;">Disabled</span>'}</p>
<hr>
<p><b>Description:</b></p>
<p>{description}</p>
        """.strip()

        self.plugin_details.setHtml(details)

        # Update button states
        self.enable_btn.setEnabled(not enabled)
        self.disable_btn.setEnabled(enabled)

    def _enable_plugin(self):
        """Enable selected plugin."""
        current = self.plugin_list.currentItem()
        if not current:
            return

        plugin = current.data(Qt.ItemDataRole.UserRole)
        if not plugin:
            return

        try:
            if hasattr(plugin, 'enable'):
                plugin.enable()
            elif hasattr(plugin, 'enabled'):
                plugin.enabled = True

            logger.info(f"Enabled plugin: {getattr(plugin, 'name', 'Unknown')}")
            QMessageBox.information(self, "Success", "Plugin enabled successfully")
            self._load_plugins()

        except Exception as e:
            logger.error(f"Failed to enable plugin: {e}")
            QMessageBox.critical(self, "Error", f"Failed to enable plugin:\n{e}")

    def _disable_plugin(self):
        """Disable selected plugin."""
        current = self.plugin_list.currentItem()
        if not current:
            return

        plugin = current.data(Qt.ItemDataRole.UserRole)
        if not plugin:
            return

        try:
            if hasattr(plugin, 'disable'):
                plugin.disable()
            elif hasattr(plugin, 'enabled'):
                plugin.enabled = False

            logger.info(f"Disabled plugin: {getattr(plugin, 'name', 'Unknown')}")
            QMessageBox.information(self, "Success", "Plugin disabled successfully")
            self._load_plugins()

        except Exception as e:
            logger.error(f"Failed to disable plugin: {e}")
            QMessageBox.critical(self, "Error", f"Failed to disable plugin:\n{e}")
