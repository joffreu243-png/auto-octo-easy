"""
Octo Browser Settings Dialog.

Dialog for configuring Octo Browser API connection.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger
import asyncio

from octomaster.integrations.octo.api_client import OctoAPIClient


class OctoSettingsDialog(QDialog):
    """Dialog for Octo Browser API settings."""

    settings_saved = pyqtSignal(dict)  # Emits settings when saved

    def __init__(self, parent=None, current_settings: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Octo Browser API Settings")
        self.setMinimumWidth(500)

        self.current_settings = current_settings or {}
        self.api_client = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>🌐 Octo Browser API Settings</h2>")
        layout.addWidget(header)

        # API Connection group
        conn_group = QGroupBox("API Connection")
        conn_layout = QFormLayout()

        # API Token
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("Enter your Octo Browser API token...")
        conn_layout.addRow("API Token:", self.token_input)

        # Show/Hide token button
        token_button_layout = QHBoxLayout()
        self.show_token_btn = QPushButton("👁️ Show")
        self.show_token_btn.setMaximumWidth(80)
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)
        token_button_layout.addWidget(self.show_token_btn)
        token_button_layout.addStretch()
        conn_layout.addRow("", token_button_layout)

        # Local API URL
        self.api_url_input = QLineEdit()
        self.api_url_input.setText("http://localhost:58888")
        self.api_url_input.setPlaceholderText("http://localhost:58888")
        conn_layout.addRow("Local API URL:", self.api_url_input)

        # Test connection button
        test_btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔍 Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        test_btn_layout.addWidget(self.test_btn)
        test_btn_layout.addStretch()
        conn_layout.addRow("", test_btn_layout)

        # Connection status
        self.status_label = QLabel("")
        conn_layout.addRow("Status:", self.status_label)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Help text
        help_text = QLabel(
            "<p><b>How to get API Token:</b></p>"
            "<ol>"
            "<li>Open Octo Browser</li>"
            "<li>Go to <b>Settings → Additional</b></li>"
            "<li>Copy your <b>API Token</b></li>"
            "</ol>"
            "<p><b>Note:</b> Octo Browser must be running for the Local API to work.</p>"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(help_text)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_settings(self):
        """Load current settings into UI."""
        if self.current_settings:
            self.token_input.setText(self.current_settings.get('api_token', ''))
            self.api_url_input.setText(self.current_settings.get('api_url', 'http://localhost:58888'))

    def toggle_token_visibility(self):
        """Toggle API token visibility."""
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_token_btn.setText("🙈 Hide")
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_token_btn.setText("👁️ Show")

    def test_connection(self):
        """Test connection to Octo Browser API."""
        token = self.token_input.text().strip()
        url = self.api_url_input.text().strip()

        if not token:
            QMessageBox.warning(self, "Missing Token", "Please enter your API token first.")
            return

        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter the Local API URL.")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.status_label.setText("🔄 Testing connection...")

        # Run async test
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._test_connection_async(token, url))
        except RuntimeError:
            # No event loop running, create one
            asyncio.run(self._test_connection_async(token, url))

    async def _test_connection_async(self, token: str, url: str):
        """Async connection test."""
        try:
            client = OctoAPIClient(api_token=token, base_url=url)
            success = await client.check_connection()

            if success:
                # Get profiles to verify full access
                profiles = await client.list_profiles()
                self.status_label.setText(f"✅ Connected! Found {len(profiles)} profiles")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")

                QMessageBox.information(
                    self,
                    "Connection Successful",
                    f"✅ Successfully connected to Octo Browser!\n\n"
                    f"Found {len(profiles)} profiles in your account."
                )
            else:
                self.status_label.setText("❌ Connection failed")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")

                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    "❌ Failed to connect to Octo Browser.\n\n"
                    "Please check:\n"
                    "1. Octo Browser is running\n"
                    "2. API token is correct\n"
                    "3. Local API URL is correct"
                )

            await client.close()

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

            QMessageBox.critical(
                self,
                "Connection Error",
                f"❌ Connection error:\n\n{str(e)}\n\n"
                "Make sure Octo Browser is running and the Local API is enabled."
            )

        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("🔍 Test Connection")

    def save_settings(self):
        """Save settings and close dialog."""
        token = self.token_input.text().strip()
        url = self.api_url_input.text().strip()

        if not token:
            QMessageBox.warning(self, "Missing Token", "Please enter your API token.")
            return

        if not url:
            url = "http://localhost:58888"

        settings = {
            'api_token': token,
            'api_url': url
        }

        # Emit signal with settings
        self.settings_saved.emit(settings)

        # Save to config file would go here
        logger.info("Octo Browser API settings saved")

        QMessageBox.information(
            self,
            "Settings Saved",
            "✅ Octo Browser API settings saved successfully!"
        )

        self.accept()

    def get_settings(self) -> dict:
        """Get current settings.

        Returns:
            Dictionary with api_token and api_url
        """
        return {
            'api_token': self.token_input.text().strip(),
            'api_url': self.api_url_input.text().strip()
        }
