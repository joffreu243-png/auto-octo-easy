"""
About dialog for OctoMaster Pro.

Displays application information and credits.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QWidget,
)


class AboutDialog(QDialog):
    """About dialog showing application information."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize about dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("About OctoMaster Pro")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Logo and title
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label = QLabel("🐙")
        logo_label.setStyleSheet("font-size: 64px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(logo_label)

        title_label = QLabel("<h1>OctoMaster Pro</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        version_label = QLabel("Version 1.0.0-alpha")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: gray;")
        title_layout.addWidget(version_label)

        layout.addLayout(title_layout)

        # Description
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        description.setMaximumHeight(150)
        description.setHtml(
            """
            <p style="text-align: center;">
            <b>Visual Automation & Web Scraping Platform</b>
            </p>
            <p>
            OctoMaster Pro is a powerful visual automation platform for creating
            web scraping workflows, browser automation, and data processing tasks
            without writing code.
            </p>
            <p style="text-align: center;">
            <a href="https://github.com/yourusername/octomaster-pro">GitHub</a> |
            <a href="https://octomaster-pro.com/docs">Documentation</a> |
            <a href="https://octomaster-pro.com">Website</a>
            </p>
            """
        )
        layout.addWidget(description)

        # Credits
        credits = QTextBrowser()
        credits.setMaximumHeight(100)
        credits.setHtml(
            """
            <p><b>Credits:</b></p>
            <ul>
            <li>Built with Python & PyQt6</li>
            <li>Powered by Playwright for browser automation</li>
            <li>Uses Pydantic for configuration management</li>
            </ul>
            """
        )
        layout.addWidget(credits)

        # Copyright
        copyright_label = QLabel(
            "© 2024 OctoMaster Pro. All rights reserved."
        )
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(copyright_label)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
