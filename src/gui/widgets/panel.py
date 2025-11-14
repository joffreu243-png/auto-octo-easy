"""
Base panel widget for OctoMaster Pro GUI.

Provides a reusable panel widget with title bar and content area.
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)


class Panel(QWidget):
    """Base panel widget with title and content area.

    Provides a titled panel that can be collapsed/expanded.
    """

    collapsed = pyqtSignal(bool)  # Emitted when panel is collapsed/expanded

    def __init__(
        self,
        title: str = "",
        collapsible: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize panel.

        Args:
            title: Panel title text
            collapsible: Whether panel can be collapsed
            parent: Parent widget
        """
        super().__init__(parent)
        self._title = title
        self._collapsible = collapsible
        self._is_collapsed = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        if self._title:
            self._title_bar = self._create_title_bar()
            layout.addWidget(self._title_bar)

        # Content area
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._content_widget)

    def _create_title_bar(self) -> QFrame:
        """Create title bar widget.

        Returns:
            Title bar widget
        """
        title_bar = QFrame()
        title_bar.setFrameShape(QFrame.Shape.StyledPanel)
        title_bar.setObjectName("panelTitleBar")

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(8, 4, 8, 4)

        # Title label
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("panelTitle")
        layout.addWidget(self._title_label)

        layout.addStretch()

        # Collapse button
        if self._collapsible:
            self._collapse_btn = QPushButton("▼")
            self._collapse_btn.setFixedSize(20, 20)
            self._collapse_btn.clicked.connect(self._toggle_collapse)
            self._collapse_btn.setToolTip("Collapse/Expand")
            layout.addWidget(self._collapse_btn)

        return title_bar

    def _toggle_collapse(self) -> None:
        """Toggle panel collapsed state."""
        self._is_collapsed = not self._is_collapsed
        self._content_widget.setVisible(not self._is_collapsed)

        if hasattr(self, "_collapse_btn"):
            self._collapse_btn.setText("▶" if self._is_collapsed else "▼")

        self.collapsed.emit(self._is_collapsed)

    @property
    def title(self) -> str:
        """Get panel title.

        Returns:
            Panel title
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set panel title.

        Args:
            value: New title
        """
        self._title = value
        if hasattr(self, "_title_label"):
            self._title_label.setText(value)

    @property
    def content_layout(self) -> QVBoxLayout:
        """Get content layout for adding widgets.

        Returns:
            Content area layout
        """
        return self._content_layout

    def set_collapsed(self, collapsed: bool) -> None:
        """Set collapsed state.

        Args:
            collapsed: Whether panel should be collapsed
        """
        if collapsed != self._is_collapsed:
            self._toggle_collapse()

    def is_collapsed(self) -> bool:
        """Check if panel is collapsed.

        Returns:
            True if collapsed
        """
        return self._is_collapsed


class TitledFrame(QFrame):
    """Simple titled frame widget."""

    def __init__(
        self, title: str = "", parent: Optional[QWidget] = None
    ) -> None:
        """Initialize titled frame.

        Args:
            title: Frame title
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._setup_ui(title)

    def _setup_ui(self, title: str) -> None:
        """Setup UI.

        Args:
            title: Frame title
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        if title:
            title_label = QLabel(f"<b>{title}</b>")
            layout.addWidget(title_label)

        self._content_layout = QVBoxLayout()
        layout.addLayout(self._content_layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        """Get content layout.

        Returns:
            Content layout
        """
        return self._content_layout
