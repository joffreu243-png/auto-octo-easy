"""
Sidebar widget for OctoMaster Pro.

Provides a project tree view with file browser and context menu.
"""

from typing import Optional
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QMenu,
    QHeaderView,
    QTabWidget,
)


class ProjectTreeView(QTreeView):
    """Tree view for project files."""

    item_double_clicked = pyqtSignal(str)  # Emits file path
    item_deleted = pyqtSignal(str)  # Emits file path

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize project tree view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._setup_model()

    def _setup_ui(self) -> None:
        """Setup tree view UI."""
        self.setHeaderHidden(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.doubleClicked.connect(self._on_double_click)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)

    def _setup_model(self) -> None:
        """Setup tree model."""
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Name", "Type"])
        self.setModel(self._model)

        # Setup header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    def load_project(self, project_path: Path) -> None:
        """Load project structure into tree.

        Args:
            project_path: Path to project directory
        """
        self._model.clear()
        self._model.setHorizontalHeaderLabels(["Name", "Type"])

        if not project_path.exists():
            return

        # Add project root
        root_item = QStandardItem(f"📁 {project_path.name}")
        root_item.setData(str(project_path), Qt.ItemDataRole.UserRole)
        self._model.appendRow([root_item, QStandardItem("Project")])

        # Add standard folders
        self._add_folder(root_item, "Workflows", "📋")
        self._add_folder(root_item, "Scripts", "📜")
        self._add_folder(root_item, "Data", "📊")
        self._add_folder(root_item, "Logs", "📝")

        self.expandAll()

    def _add_folder(
        self, parent: QStandardItem, name: str, icon: str = "📁"
    ) -> QStandardItem:
        """Add folder to tree.

        Args:
            parent: Parent item
            name: Folder name
            icon: Folder icon (emoji)

        Returns:
            Created folder item
        """
        folder_item = QStandardItem(f"{icon} {name}")
        folder_item.setData(name, Qt.ItemDataRole.UserRole)
        type_item = QStandardItem("Folder")
        parent.appendRow([folder_item, type_item])
        return folder_item

    def add_file(self, folder_name: str, file_name: str, file_type: str) -> None:
        """Add file to specific folder.

        Args:
            folder_name: Name of folder to add file to
            file_name: Name of file
            file_type: Type of file
        """
        root = self._model.item(0)
        if not root:
            return

        # Find folder
        for i in range(root.rowCount()):
            folder = root.child(i, 0)
            if folder and folder_name in folder.text():
                # Add file
                file_item = QStandardItem(f"📄 {file_name}")
                file_item.setData(file_name, Qt.ItemDataRole.UserRole)
                type_item = QStandardItem(file_type)
                folder.appendRow([file_item, type_item])
                break

    def _on_double_click(self, index) -> None:
        """Handle item double click.

        Args:
            index: Clicked index
        """
        item = self._model.itemFromIndex(index)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and "📄" in item.text():
                self.item_double_clicked.emit(data)

    def _show_context_menu(self, position) -> None:
        """Show context menu for item.

        Args:
            position: Menu position
        """
        index = self.indexAt(position)
        if not index.isValid():
            return

        item = self._model.itemFromIndex(index)
        if not item:
            return

        menu = QMenu(self)

        # Check if it's a file or folder
        is_file = "📄" in item.text()
        is_folder = "📁" in item.text() or "📋" in item.text()

        if is_file:
            open_action = QAction("Open", self)
            open_action.triggered.connect(
                lambda: self.item_double_clicked.emit(
                    item.data(Qt.ItemDataRole.UserRole)
                )
            )
            menu.addAction(open_action)

            menu.addSeparator()

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(
                lambda: self.item_deleted.emit(item.data(Qt.ItemDataRole.UserRole))
            )
            menu.addAction(delete_action)

        elif is_folder:
            new_file_action = QAction("New File", self)
            menu.addAction(new_file_action)

            menu.addSeparator()

            refresh_action = QAction("Refresh", self)
            menu.addAction(refresh_action)

        menu.exec(self.viewport().mapToGlobal(position))


class SideBar(QWidget):
    """Sidebar widget with tabbed views."""

    file_opened = pyqtSignal(str)  # Emits file path

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize sidebar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for different views
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Project tree
        self._project_tree = ProjectTreeView()
        self._project_tree.item_double_clicked.connect(self.file_opened.emit)
        self._tabs.addTab(self._project_tree, "📁 Files")

        # TODO: Add more tabs (Scripts, Data, etc.)

    @property
    def project_tree(self) -> ProjectTreeView:
        """Get project tree view.

        Returns:
            Project tree view widget
        """
        return self._project_tree

    def load_project(self, project_path: Path) -> None:
        """Load project into sidebar.

        Args:
            project_path: Path to project
        """
        self._project_tree.load_project(project_path)
