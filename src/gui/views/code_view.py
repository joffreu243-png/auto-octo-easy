"""
Code editor view for OctoMaster Pro.

Provides a code editor with line numbers and basic syntax highlighting.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QTextFormat,
    QFont,
    QPaintEvent,
    QResizeEvent,
)
from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit


class LineNumberArea(QWidget):
    """Line number area widget for code editor."""

    def __init__(self, editor: "CodeEditor") -> None:
        """Initialize line number area.

        Args:
            editor: Parent code editor
        """
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        """Get size hint.

        Returns:
            Preferred size
        """
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint line numbers.

        Args:
            event: Paint event
        """
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize code editor.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Setup font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Setup tab width
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(' ') * 4
        )

    def line_number_area_width(self) -> int:
        """Calculate line number area width.

        Returns:
            Width in pixels
        """
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _: int) -> None:
        """Update line number area width.

        Args:
            _: Block count (unused)
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        """Update line number area on scroll.

        Args:
            rect: Update rectangle
            dy: Vertical scroll delta
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize event.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """Paint line numbers.

        Args:
            event: Paint event
        """
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(240, 240, 240))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(128, 128, 128))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self) -> None:
        """Highlight the current line."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.GlobalColor.yellow).lighter(190)

            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class CodeView(QWidget):
    """Code view widget."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize code view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI."""
        from PyQt6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._editor = CodeEditor()
        layout.addWidget(self._editor)

    @property
    def editor(self) -> CodeEditor:
        """Get code editor.

        Returns:
            Code editor widget
        """
        return self._editor

    def set_text(self, text: str) -> None:
        """Set editor text.

        Args:
            text: Text to set
        """
        self._editor.setPlainText(text)

    def get_text(self) -> str:
        """Get editor text.

        Returns:
            Current text
        """
        return self._editor.toPlainText()

    def clear(self) -> None:
        """Clear editor."""
        self._editor.clear()
