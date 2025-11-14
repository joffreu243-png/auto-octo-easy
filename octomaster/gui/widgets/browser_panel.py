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
    QTextEdit,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from loguru import logger

# Try to import WebEngine, fallback to error message if not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    logger.warning(f"QWebEngineView not available: {e}")


class BrowserPanel(QWidget):
    """Browser panel with embedded Chromium view."""

    url_changed = pyqtSignal(str)
    page_loaded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.web_view = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not WEBENGINE_AVAILABLE:
            # Show error message if WebEngine not available
            error_label = QLabel(
                "<h2>Browser Preview Not Available</h2>"
                "<p>QWebEngineView could not be loaded. This is usually due to:</p>"
                "<ul>"
                "<li>Missing PyQt6-WebEngine package</li>"
                "<li>GPU rendering issues in virtual machines</li>"
                "<li>Missing system dependencies</li>"
                "</ul>"
                "<p><b>Workaround:</b> Use the Workflow Executor to run automations in Playwright browser.</p>"
                "<p><b>To fix:</b> Install PyQt6-WebEngine or disable GPU acceleration.</p>"
            )
            error_label.setWordWrap(True)
            error_label.setStyleSheet("padding: 20px; background-color: #fff3cd; border: 2px solid #ffc107;")
            layout.addWidget(error_label)
            return

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

        # Web view - wrapped in try-except for safety
        try:
            self.web_view = QWebEngineView()
            self.web_view.urlChanged.connect(self.on_url_changed)
            self.web_view.loadFinished.connect(self.on_load_finished)
            layout.addWidget(self.web_view)
            logger.info("Browser panel initialized successfully")
        except Exception as e:
            logger.error(f"Failed to create QWebEngineView: {e}")
            error_text = QTextEdit()
            error_text.setReadOnly(True)
            error_text.setHtml(
                f"<h3>Failed to initialize browser</h3>"
                f"<p>Error: {e}</p>"
                f"<p>Use Playwright executor instead for automation.</p>"
            )
            layout.addWidget(error_text)
            return

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 3px;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

    def navigate_to_url(self):
        """Navigate to the URL in the address bar."""
        if not self.web_view:
            logger.warning("WebView not available")
            return

        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        logger.info(f"Navigating to: {url}")
        self.web_view.setUrl(QUrl(url))
        self.status_label.setText("Loading...")

    def go_back(self):
        """Go back in browser history."""
        if self.web_view:
            self.web_view.back()

    def go_forward(self):
        """Go forward in browser history."""
        if self.web_view:
            self.web_view.forward()

    def refresh(self):
        """Refresh the current page."""
        if self.web_view:
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
            if self.web_view:
                url = self.web_view.url().toString()
                self.page_loaded.emit(url)
                logger.info(f"Page loaded: {url}")
        else:
            self.status_label.setText("Failed to load")
            logger.error("Page failed to load")
