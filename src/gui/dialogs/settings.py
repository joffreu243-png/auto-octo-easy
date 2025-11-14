"""
Settings dialog for OctoMaster Pro.

Dialog for application settings and preferences.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QTabWidget,
    QWidget,
    QGroupBox,
    QDialogButtonBox,
    QPushButton,
)

from src.gui.styles.themes import ThemeType, get_theme_manager
from loguru import logger


class SettingsDialog(QDialog):
    """Settings dialog."""

    def __init__(self, config=None, parent: Optional[QWidget] = None) -> None:
        """Initialize settings dialog.

        Args:
            config: Application configuration object
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self._setup_ui()
        if self.config:
            self._load_settings()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Tab widget for different settings categories
        tabs = QTabWidget()

        # General settings
        tabs.addTab(self._create_general_tab(), "General")

        # Editor settings
        tabs.addTab(self._create_editor_tab(), "Editor")

        # Workflow settings
        tabs.addTab(self._create_workflow_tab(), "Workflow")

        # Browser settings
        tabs.addTab(self._create_browser_tab(), "Browser")

        layout.addWidget(tabs)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_settings
        )

        layout.addWidget(button_box)

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab.

        Returns:
            General settings widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)

        theme_label = QLabel("Theme:")
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light"])

        current_theme = get_theme_manager().current_theme
        self._theme_combo.setCurrentText(
            "Dark" if current_theme == ThemeType.DARK else "Light"
        )

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self._theme_combo)

        layout.addWidget(theme_group)

        # Auto-save
        autosave_group = QGroupBox("Auto-save")
        autosave_layout = QVBoxLayout(autosave_group)

        self._autosave_check = QCheckBox("Enable auto-save")
        self._autosave_check.setChecked(True)
        autosave_layout.addWidget(self._autosave_check)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Auto-save interval (minutes):"))
        self._autosave_spin = QSpinBox()
        self._autosave_spin.setRange(1, 60)
        self._autosave_spin.setValue(5)
        interval_layout.addWidget(self._autosave_spin)
        interval_layout.addStretch()

        autosave_layout.addLayout(interval_layout)

        layout.addWidget(autosave_group)

        layout.addStretch()
        return widget

    def _create_editor_tab(self) -> QWidget:
        """Create editor settings tab.

        Returns:
            Editor settings widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout(font_group)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font size:"))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 24)
        self._font_size_spin.setValue(10)
        size_layout.addWidget(self._font_size_spin)
        size_layout.addStretch()

        font_layout.addLayout(size_layout)

        layout.addWidget(font_group)

        # Editor options
        options_group = QGroupBox("Editor Options")
        options_layout = QVBoxLayout(options_group)

        self._line_numbers_check = QCheckBox("Show line numbers")
        self._line_numbers_check.setChecked(True)
        options_layout.addWidget(self._line_numbers_check)

        self._word_wrap_check = QCheckBox("Enable word wrap")
        options_layout.addWidget(self._word_wrap_check)

        layout.addWidget(options_group)

        layout.addStretch()
        return widget

    def _create_workflow_tab(self) -> QWidget:
        """Create workflow settings tab.

        Returns:
            Workflow settings widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Execution settings
        exec_group = QGroupBox("Execution")
        exec_layout = QVBoxLayout(exec_group)

        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Default timeout (seconds):"))
        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(1, 300)
        self._timeout_spin.setValue(30)
        timeout_layout.addWidget(self._timeout_spin)
        timeout_layout.addStretch()

        exec_layout.addLayout(timeout_layout)

        self._stop_on_error_check = QCheckBox("Stop workflow on error")
        self._stop_on_error_check.setChecked(True)
        exec_layout.addWidget(self._stop_on_error_check)

        layout.addWidget(exec_group)

        layout.addStretch()
        return widget

    def _create_browser_tab(self) -> QWidget:
        """Create browser settings tab.

        Returns:
            Browser settings widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Browser options
        browser_group = QGroupBox("Browser Options")
        browser_layout = QVBoxLayout(browser_group)

        self._headless_check = QCheckBox("Run browser in headless mode")
        browser_layout.addWidget(self._headless_check)

        self._disable_images_check = QCheckBox("Disable image loading")
        browser_layout.addWidget(self._disable_images_check)

        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Page load timeout (seconds):"))
        self._page_timeout_spin = QSpinBox()
        self._page_timeout_spin.setRange(5, 120)
        self._page_timeout_spin.setValue(30)
        timeout_layout.addWidget(self._page_timeout_spin)
        timeout_layout.addStretch()

        browser_layout.addLayout(timeout_layout)

        layout.addWidget(browser_group)

        layout.addStretch()
        return widget

    def _apply_settings(self) -> None:
        """Apply settings without closing dialog."""
        try:
            # Apply theme
            theme_text = self._theme_combo.currentText()
            theme = ThemeType.DARK if theme_text == "Dark" else ThemeType.LIGHT
            get_theme_manager().set_theme(theme)
            logger.debug(f"Applied theme: {theme_text}")

            if not self.config:
                logger.warning("No config object provided, settings not saved")
                return

            # Apply general settings
            self.config.set('autosave_enabled', self._autosave_check.isChecked())
            self.config.set('autosave_interval', self._autosave_spin.value())

            # Apply editor settings
            self.config.set('font_size', self._font_size_spin.value())
            self.config.set('show_line_numbers', self._line_numbers_check.isChecked())
            self.config.set('word_wrap', self._word_wrap_check.isChecked())

            # Apply workflow settings
            self.config.set('default_timeout', self._timeout_spin.value())
            self.config.set('stop_on_error', self._stop_on_error_check.isChecked())

            # Apply browser settings
            self.config.set('headless', self._headless_check.isChecked())
            self.config.set('disable_images', self._disable_images_check.isChecked())
            self.config.set('browser_timeout', self._page_timeout_spin.value() * 1000)  # Convert to ms

            logger.info("Settings applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")

    def _load_settings(self) -> None:
        """Load settings from config."""
        try:
            if not self.config:
                return

            # Load general settings
            self._autosave_check.setChecked(self.config.get('autosave_enabled', True))
            self._autosave_spin.setValue(self.config.get('autosave_interval', 5))

            # Load editor settings
            self._font_size_spin.setValue(self.config.get('font_size', 10))
            self._line_numbers_check.setChecked(self.config.get('show_line_numbers', True))
            self._word_wrap_check.setChecked(self.config.get('word_wrap', False))

            # Load workflow settings
            self._timeout_spin.setValue(self.config.get('default_timeout', 30))
            self._stop_on_error_check.setChecked(self.config.get('stop_on_error', True))

            # Load browser settings
            self._headless_check.setChecked(self.config.get('headless', False))
            self._disable_images_check.setChecked(self.config.get('disable_images', False))
            self._page_timeout_spin.setValue(self.config.get('browser_timeout', 30000) // 1000)  # Convert from ms

            logger.debug("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
