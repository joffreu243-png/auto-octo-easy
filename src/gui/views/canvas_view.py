"""
Canvas view for node editor in OctoMaster Pro.

Provides a graphics view for visual workflow editing with zoom, pan, and grid.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QWheelEvent,
    QMouseEvent,
    QKeyEvent,
)
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QWidget


class CanvasView(QGraphicsView):
    """Graphics view for node editor canvas.

    Supports zoom, pan, grid background, and node placement.
    """

    zoom_changed = pyqtSignal(float)  # Emits zoom level
    selection_changed = pyqtSignal(list)  # Emits selected items

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize canvas view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._zoom = 1.0
        self._zoom_min = 0.1
        self._zoom_max = 5.0
        self._zoom_step = 1.15
        self._pan_active = False
        self._pan_start_pos = None
        self._grid_size = 20
        self._show_grid = True
        self._setup_scene()
        self._setup_view()

    def _setup_scene(self) -> None:
        """Setup graphics scene."""
        self._scene = QGraphicsScene(self)
        self._scene.setSceneRect(-5000, -5000, 10000, 10000)
        self._scene.selectionChanged.connect(self._on_selection_changed)
        self.setScene(self._scene)

    def _setup_view(self) -> None:
        """Setup view settings."""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw grid background.

        Args:
            painter: QPainter instance
            rect: Rectangle to draw
        """
        super().drawBackground(painter, rect)

        if not self._show_grid:
            return

        # Draw grid
        left = int(rect.left()) - (int(rect.left()) % self._grid_size)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size)

        # Grid lines
        lines = []
        x = left
        while x < rect.right():
            lines.append((x, rect.top(), x, rect.bottom()))
            x += self._grid_size

        y = top
        while y < rect.bottom():
            lines.append((rect.left(), y, rect.right(), y))
            y += self._grid_size

        # Draw grid lines
        pen = QPen(QColor(80, 80, 80, 80))
        pen.setWidth(0)
        painter.setPen(pen)
        for x1, y1, x2, y2 in lines:
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw major grid lines (every 5th line)
        pen = QPen(QColor(100, 100, 100, 100))
        pen.setWidth(0)
        painter.setPen(pen)

        major_size = self._grid_size * 5
        x = left - (left % major_size)
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += major_size

        y = top - (top % major_size)
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += major_size

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming.

        Args:
            event: Wheel event
        """
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl + Wheel
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning with middle mouse button
            self._pan_active = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events.

        Args:
            event: Mouse event
        """
        if self._pan_active and self._pan_start_pos:
            # Pan the view
            delta = event.pos() - self._pan_start_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self._pan_start_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_active:
            # Stop panning
            self._pan_active = False
            self._pan_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events.

        Args:
            event: Key event
        """
        if event.key() == Qt.Key.Key_Space:
            # Pan mode with spacebar
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            # Delete selected items
            self.delete_selected()
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """Handle key release events.

        Args:
            event: Key event
        """
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def zoom_in(self) -> None:
        """Zoom in the view."""
        if self._zoom * self._zoom_step <= self._zoom_max:
            self.scale(self._zoom_step, self._zoom_step)
            self._zoom *= self._zoom_step
            self.zoom_changed.emit(self._zoom)

    def zoom_out(self) -> None:
        """Zoom out the view."""
        if self._zoom / self._zoom_step >= self._zoom_min:
            self.scale(1 / self._zoom_step, 1 / self._zoom_step)
            self._zoom /= self._zoom_step
            self.zoom_changed.emit(self._zoom)

    def zoom_reset(self) -> None:
        """Reset zoom to 100%."""
        self.resetTransform()
        self._zoom = 1.0
        self.zoom_changed.emit(self._zoom)

    def set_zoom(self, zoom: float) -> None:
        """Set specific zoom level.

        Args:
            zoom: Zoom level (1.0 = 100%)
        """
        if self._zoom_min <= zoom <= self._zoom_max:
            self.resetTransform()
            self.scale(zoom, zoom)
            self._zoom = zoom
            self.zoom_changed.emit(self._zoom)

    def get_zoom(self) -> float:
        """Get current zoom level.

        Returns:
            Current zoom level
        """
        return self._zoom

    def set_grid_visible(self, visible: bool) -> None:
        """Set grid visibility.

        Args:
            visible: Whether grid should be visible
        """
        self._show_grid = visible
        self.viewport().update()

    def is_grid_visible(self) -> bool:
        """Check if grid is visible.

        Returns:
            True if grid is visible
        """
        return self._show_grid

    def delete_selected(self) -> None:
        """Delete selected items from scene."""
        for item in self._scene.selectedItems():
            self._scene.removeItem(item)

    def clear_scene(self) -> None:
        """Clear all items from scene."""
        self._scene.clear()

    def _on_selection_changed(self) -> None:
        """Handle selection change."""
        selected = self._scene.selectedItems()
        self.selection_changed.emit(selected)

    def fit_in_view(self) -> None:
        """Fit all items in view."""
        items_rect = self._scene.itemsBoundingRect()
        if not items_rect.isEmpty():
            self.fitInView(items_rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = self.transform().m11()
            self.zoom_changed.emit(self._zoom)

    @property
    def scene(self) -> QGraphicsScene:
        """Get graphics scene.

        Returns:
            Graphics scene
        """
        return self._scene
