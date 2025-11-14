"""
Browser Panel widget.

Embedded browser view with controls.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QToolBar,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from loguru import logger


class BrowserPanel(QWidget):
    """Browser panel with embedded Chromium view."""

    url_changed = pyqtSignal(str)
    page_loaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Back button
        back_btn = QPushButton("◀")
        back_btn.setMaximumWidth(30)
        back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(back_btn)

        # Forward button
        forward_btn = QPushButton("▶")
        forward_btn.setMaximumWidth(30)
        forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_btn)

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Go button
        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self.navigate_to_url)
        toolbar.addWidget(go_btn)

        layout.addWidget(toolbar)

        # Web view
        self.web_view = QWebEngineView()
        self.web_view.urlChanged.connect(self.on_url_changed)
        self.web_view.loadFinished.connect(self.on_load_finished)
        layout.addWidget(self.web_view)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 3px;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

    def navigate_to_url(self):
        """Navigate to the URL in the address bar."""
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        logger.info(f"Navigating to: {url}")
        self.web_view.setUrl(QUrl(url))
        self.status_label.setText("Loading...")

    def go_back(self):
        """Go back in browser history."""
        self.web_view.back()

    def go_forward(self):
        """Go forward in browser history."""
        self.web_view.forward()

    def refresh(self):
        """Refresh the current page."""
        self.web_view.reload()

    def on_url_changed(self, url: QUrl):
        """Handle URL change."""
        url_str = url.toString()
        self.url_bar.setText(url_str)
        self.url_changed.emit(url_str)
        logger.debug(f"URL changed: {url_str}")

    def on_load_finished(self, success: bool):
        """Handle page load finished."""
        if success:
            self.status_label.setText("Done")
            url = self.web_view.url().toString()
            self.page_loaded.emit(url)
            logger.info(f"Page loaded: {url}")
        else:
            self.status_label.setText("Failed to load")
            logger.error("Page failed to load")
