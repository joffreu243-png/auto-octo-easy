"""
Browser Panel widget.

Embedded browser view with controls and element inspector.
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
    QMenu,
    QInputDialog,
    QDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QAction
from loguru import logger
import json

# Try to import WebEngine, fallback to error message if not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    logger.warning(f"QWebEngineView not available: {e}")


# JavaScript code for element inspector
INSPECTOR_JS = """
(function() {
    window.inspectorEnabled = false;
    window.currentHighlightedElement = null;
    window.highlightOverlay = null;

    // Generate best selector for element
    window.generateSelector = function(element) {
        // Priority: ID > data-testid > unique class > tag + nth-child
        if (element.id) {
            return '#' + element.id;
        }

        if (element.hasAttribute('data-testid')) {
            return '[data-testid="' + element.getAttribute('data-testid') + '"]';
        }

        if (element.hasAttribute('data-test')) {
            return '[data-test="' + element.getAttribute('data-test') + '"]';
        }

        // Try to find unique class combination
        if (element.className) {
            const classes = element.className.split(' ').filter(c => c);
            if (classes.length > 0) {
                const selector = element.tagName.toLowerCase() + '.' + classes.join('.');
                if (document.querySelectorAll(selector).length === 1) {
                    return selector;
                }
            }
        }

        // Fallback: tag + nth-child path
        let path = [];
        let current = element;
        while (current.parentElement) {
            let index = Array.from(current.parentElement.children).indexOf(current) + 1;
            path.unshift(current.tagName.toLowerCase() + ':nth-child(' + index + ')');
            current = current.parentElement;
            if (current.id) {
                path.unshift('#' + current.id);
                break;
            }
        }
        return path.join(' > ');
    };

    // Get element info
    window.getElementInfo = function(element) {
        return {
            tagName: element.tagName.toLowerCase(),
            id: element.id || '',
            className: element.className || '',
            text: element.textContent.trim().substring(0, 100),
            selector: window.generateSelector(element),
            href: element.href || '',
            value: element.value || '',
            type: element.type || '',
            placeholder: element.placeholder || ''
        };
    };

    // Highlight element
    window.highlightElement = function(element) {
        if (!element || element === document.body || element === document.documentElement) {
            return;
        }

        window.clearHighlight();
        window.currentHighlightedElement = element;

        // Create highlight overlay
        const rect = element.getBoundingClientRect();
        window.highlightOverlay = document.createElement('div');
        window.highlightOverlay.style.cssText = `
            position: fixed;
            top: ${rect.top}px;
            left: ${rect.left}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            border: 2px solid #ff0000;
            background: rgba(255, 0, 0, 0.1);
            pointer-events: none;
            z-index: 999999;
            box-sizing: border-box;
        `;
        document.body.appendChild(window.highlightOverlay);
    };

    // Clear highlight
    window.clearHighlight = function() {
        if (window.highlightOverlay) {
            window.highlightOverlay.remove();
            window.highlightOverlay = null;
        }
        window.currentHighlightedElement = null;
    };

    // Mouse move handler
    window.inspectorMouseMove = function(e) {
        if (!window.inspectorEnabled) return;

        const element = document.elementFromPoint(e.clientX, e.clientY);
        if (element && element !== window.currentHighlightedElement) {
            window.highlightElement(element);

            // Send to Python
            if (window.pybridge) {
                const info = window.getElementInfo(element);
                window.pybridge.onElementHovered(JSON.stringify(info));
            }
        }
    };

    // Mouse click handler (right click for context menu)
    window.inspectorMouseDown = function(e) {
        if (!window.inspectorEnabled) return;

        // Right click
        if (e.button === 2) {
            e.preventDefault();
            e.stopPropagation();

            const element = document.elementFromPoint(e.clientX, e.clientY);
            if (element && window.pybridge) {
                const info = window.getElementInfo(element);
                window.pybridge.onElementClicked(JSON.stringify(info));
            }
            return false;
        }

        // Left click - also send for potential use
        if (e.button === 0) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    };

    // Toggle inspector mode
    window.toggleInspector = function(enabled) {
        window.inspectorEnabled = enabled;

        if (enabled) {
            document.body.style.cursor = 'crosshair';
            document.addEventListener('mousemove', window.inspectorMouseMove, true);
            document.addEventListener('mousedown', window.inspectorMouseDown, true);
            document.addEventListener('contextmenu', function(e) {
                if (window.inspectorEnabled) {
                    e.preventDefault();
                    return false;
                }
            }, true);
        } else {
            document.body.style.cursor = '';
            document.removeEventListener('mousemove', window.inspectorMouseMove, true);
            document.removeEventListener('mousedown', window.inspectorMouseDown, true);
            window.clearHighlight();
        }
    };

    console.log('OctoMaster Inspector initialized');
})();
"""


class JavaScriptBridge(QObject):
    """Bridge between JavaScript and Python."""

    element_hovered = pyqtSignal(dict)
    element_clicked = pyqtSignal(dict)

    @pyqtSlot(str)
    def onElementHovered(self, json_str):
        """Called when element is hovered in inspector mode."""
        try:
            data = json.loads(json_str)
            self.element_hovered.emit(data)
        except Exception as e:
            logger.error(f"Failed to parse element hover data: {e}")

    @pyqtSlot(str)
    def onElementClicked(self, json_str):
        """Called when element is clicked in inspector mode."""
        try:
            data = json.loads(json_str)
            self.element_clicked.emit(data)
        except Exception as e:
            logger.error(f"Failed to parse element click data: {e}")


class BrowserPanel(QWidget):
    """Browser panel with embedded Chromium view and element inspector."""

    url_changed = pyqtSignal(str)
    page_loaded = pyqtSignal(str)
    element_selected = pyqtSignal(dict)  # Emits {type: block_type, selector: css_selector, element_info: dict}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.web_view = None
        self.js_bridge = None
        self.channel = None
        self.inspector_enabled = False
        self.current_element = None
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
        back_btn.setToolTip("Back")
        back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(back_btn)

        # Forward button
        forward_btn = QPushButton("▶")
        forward_btn.setMaximumWidth(30)
        forward_btn.setToolTip("Forward")
        forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_btn)

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.setToolTip("Refresh")
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

        # Inspector button (toggle)
        self.inspector_btn = QPushButton("🎯 Inspector")
        self.inspector_btn.setCheckable(True)
        self.inspector_btn.setToolTip("Toggle element inspector mode")
        self.inspector_btn.clicked.connect(self.toggle_inspector)
        toolbar.addWidget(self.inspector_btn)

        # Popup button
        popup_btn = QPushButton("🪟 Popup")
        popup_btn.setToolTip("Open browser in popup window")
        popup_btn.clicked.connect(self.open_popup_browser)
        toolbar.addWidget(popup_btn)

        layout.addWidget(toolbar)

        # Web view - wrapped in try-except for safety
        try:
            self.web_view = QWebEngineView()
            self.web_view.urlChanged.connect(self.on_url_changed)
            self.web_view.loadFinished.connect(self.on_load_finished)

            # Setup QWebChannel for JavaScript bridge
            self.setup_web_channel()

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

    def setup_web_channel(self):
        """Setup QWebChannel for JavaScript communication."""
        try:
            if not self.web_view:
                return

            # Create JavaScript bridge
            self.js_bridge = JavaScriptBridge()
            self.js_bridge.element_hovered.connect(self.on_element_hovered)
            self.js_bridge.element_clicked.connect(self.on_element_clicked)

            # Create and setup channel
            self.channel = QWebChannel()
            self.channel.registerObject("pybridge", self.js_bridge)

            # Set channel to page
            self.web_view.page().setWebChannel(self.channel)

            logger.debug("QWebChannel setup complete")

        except Exception as e:
            logger.error(f"Failed to setup QWebChannel: {e}")

    def inject_inspector_script(self):
        """Inject inspector JavaScript into the page."""
        if not self.web_view:
            return

        try:
            # Inject qwebchannel.js first
            qwebchannel_js = """
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pybridge = channel.objects.pybridge;
                console.log('QWebChannel ready');
            });
            """

            self.web_view.page().runJavaScript(qwebchannel_js, lambda _: None)

            # Then inject inspector script
            self.web_view.page().runJavaScript(INSPECTOR_JS, lambda _: None)

            logger.debug("Inspector script injected")

        except Exception as e:
            logger.error(f"Failed to inject inspector script: {e}")

    def toggle_inspector(self, enabled):
        """Toggle inspector mode."""
        self.inspector_enabled = enabled

        if not self.web_view:
            self.inspector_btn.setChecked(False)
            return

        try:
            # Call JavaScript to toggle inspector
            js_code = f"window.toggleInspector({str(enabled).lower()});"
            self.web_view.page().runJavaScript(js_code)

            if enabled:
                self.status_label.setText("Inspector mode: Right-click on element to inspect")
                self.inspector_btn.setText("🎯 Inspector ON")
                logger.info("Inspector mode enabled")
            else:
                self.status_label.setText("Inspector mode disabled")
                self.inspector_btn.setText("🎯 Inspector")
                logger.info("Inspector mode disabled")

        except Exception as e:
            logger.error(f"Failed to toggle inspector: {e}")
            self.inspector_btn.setChecked(False)

    def on_element_hovered(self, element_info):
        """Handle element hover."""
        self.current_element = element_info
        # Update status with element info
        tag = element_info.get('tagName', '')
        text = element_info.get('text', '')[:30]
        self.status_label.setText(f"<{tag}> {text}...")

    def on_element_clicked(self, element_info):
        """Handle element click - show context menu."""
        self.current_element = element_info
        logger.info(f"Element clicked: {element_info.get('selector', '')}")

        # Show context menu
        self.show_context_menu()

    def show_context_menu(self):
        """Show context menu for element actions."""
        if not self.current_element:
            return

        menu = QMenu(self)

        # Element info section
        info_text = f"<{self.current_element.get('tagName', '')}> {self.current_element.get('selector', '')}"
        info_action = menu.addAction(info_text)
        info_action.setEnabled(False)

        menu.addSeparator()

        # Actions section
        actions_menu = menu.addMenu("🖱️ Actions")
        actions_menu.addAction("Click", lambda: self.add_block_action('click'))
        actions_menu.addAction("Double Click", lambda: self.add_block_action('double_click'))
        actions_menu.addAction("Hover", lambda: self.add_block_action('hover'))

        # Input section
        input_menu = menu.addMenu("⌨️ Input")
        input_menu.addAction("Type Text", lambda: self.add_block_action('type_text'))
        input_menu.addAction("Clear", lambda: self.add_block_action('clear'))

        # Data extraction section
        data_menu = menu.addMenu("📊 Extract Data")
        data_menu.addAction("Get Text", lambda: self.add_block_action('get_text'))
        data_menu.addAction("Get Attribute", lambda: self.add_block_action('get_attribute'))
        data_menu.addAction("Get HTML", lambda: self.add_block_action('get_html'))

        # Wait section
        wait_menu = menu.addMenu("⏱️ Wait")
        wait_menu.addAction("Wait For Element", lambda: self.add_block_action('wait_for_element'))
        wait_menu.addAction("Wait For Disappear", lambda: self.add_block_action('wait_for_disappear'))

        menu.addSeparator()

        # Copy section
        copy_menu = menu.addMenu("📋 Copy")
        copy_menu.addAction("CSS Selector", lambda: self.copy_selector())
        copy_menu.addAction("Element Text", lambda: self.copy_text())

        # Show menu at cursor position
        from PyQt6.QtGui import QCursor
        menu.exec(QCursor.pos())

    def add_block_action(self, action_type):
        """Add block based on action type."""
        if not self.current_element:
            return

        selector = self.current_element.get('selector', '')

        # Create block data
        block_data = {
            'type': action_type,
            'selector': selector,
            'element_info': self.current_element
        }

        # For type_text, ask for text input
        if action_type == 'type_text':
            text, ok = QInputDialog.getText(
                self,
                "Type Text",
                f"Enter text to type into element:\n{selector}",
                text=self.current_element.get('placeholder', '')
            )
            if ok and text:
                block_data['text'] = text
            else:
                return  # User cancelled

        # For get_attribute, ask for attribute name
        elif action_type == 'get_attribute':
            attr, ok = QInputDialog.getText(
                self,
                "Get Attribute",
                "Enter attribute name to extract:",
                text="value"
            )
            if ok and attr:
                block_data['attribute'] = attr
            else:
                return

        # Emit signal
        self.element_selected.emit(block_data)
        logger.info(f"Block action added: {action_type} on {selector}")

    def copy_selector(self):
        """Copy CSS selector to clipboard."""
        if self.current_element:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_element.get('selector', ''))
            self.status_label.setText("Selector copied to clipboard")

    def copy_text(self):
        """Copy element text to clipboard."""
        if self.current_element:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_element.get('text', ''))
            self.status_label.setText("Text copied to clipboard")

    def open_popup_browser(self):
        """Open browser in popup window."""
        try:
            popup = BrowserPopupWindow(parent=self)
            popup.element_selected.connect(self.element_selected.emit)  # Forward signal
            popup.show()
            logger.info("Opened popup browser window")
        except Exception as e:
            logger.error(f"Failed to open popup browser: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open popup browser:\n{e}")

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

            # Inject inspector script
            self.inject_inspector_script()

            # Re-enable inspector if it was enabled
            if self.inspector_enabled:
                self.toggle_inspector(True)

            if self.web_view:
                url = self.web_view.url().toString()
                self.page_loaded.emit(url)
                logger.info(f"Page loaded: {url}")
        else:
            self.status_label.setText("Failed to load")
            logger.error("Page failed to load")


class BrowserPopupWindow(QDialog):
    """Popup browser window with same functionality as embedded browser."""

    element_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OctoMaster Pro - Browser")
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(1200, 800)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create browser panel
        self.browser_panel = BrowserPanel(self)
        self.browser_panel.element_selected.connect(self.element_selected.emit)
        layout.addWidget(self.browser_panel)

        logger.info("Popup browser window created")
