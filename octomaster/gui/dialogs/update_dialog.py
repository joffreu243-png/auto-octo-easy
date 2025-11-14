"""
Update Dialog.

Dialog for checking and installing updates for OctoMaster Pro.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from loguru import logger
from pathlib import Path

from octomaster.core.updater import AutoUpdater, UpdateInfo


class UpdateCheckThread(QThread):
    """Thread for checking updates in background."""

    finished = pyqtSignal(object)  # Emits UpdateInfo or None
    error = pyqtSignal(str)

    def __init__(self, updater: AutoUpdater):
        super().__init__()
        self.updater = updater

    def run(self):
        """Check for updates."""
        try:
            update_info = self.updater.check_for_updates()
            self.finished.emit(update_info)
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            self.error.emit(str(e))


class UpdateInstallThread(QThread):
    """Thread for installing updates in background."""

    finished = pyqtSignal(bool, str)  # Emits (success, message)
    progress = pyqtSignal(str)  # Emits progress messages

    def __init__(self, updater: AutoUpdater, install_deps: bool = True):
        super().__init__()
        self.updater = updater
        self.install_deps = install_deps

    def run(self):
        """Install updates."""
        try:
            # Pull updates
            self.progress.emit("📥 Downloading updates...")
            success, message = self.updater.pull_updates()

            if not success:
                self.finished.emit(False, message)
                return

            # Install dependencies if requested
            if self.install_deps:
                self.progress.emit("📦 Installing dependencies...")
                dep_success, dep_message = self.updater.install_dependencies()

                if not dep_success:
                    message += f"\n\n⚠️ Dependencies update failed: {dep_message}"

            self.finished.emit(True, message)

        except Exception as e:
            logger.error(f"Update installation failed: {e}")
            self.finished.emit(False, f"Update failed: {str(e)}")


class UpdateDialog(QDialog):
    """Dialog for checking and installing updates."""

    def __init__(self, project_root: Path, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.updater = AutoUpdater(project_root)
        self.update_info = None

        self.setWindowTitle("Check for Updates")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.setup_ui()

        # Start checking for updates automatically
        self.check_for_updates()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>🔄 OctoMaster Pro Updates</h2>")
        layout.addWidget(header)

        # Status label
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Changelog/info area
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(200)
        layout.addWidget(self.info_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.check_btn = QPushButton("🔍 Check Again")
        self.check_btn.clicked.connect(self.check_for_updates)
        self.check_btn.setEnabled(False)
        button_layout.addWidget(self.check_btn)

        self.update_btn = QPushButton("⬇️ Install Update")
        self.update_btn.clicked.connect(self.install_updates)
        self.update_btn.setEnabled(False)
        button_layout.addWidget(self.update_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def check_for_updates(self):
        """Check for updates in background thread."""
        if not self.updater.is_git_repo():
            self.status_label.setText("❌ Not a Git repository")
            self.info_text.setPlainText(
                "This installation is not a Git repository.\n\n"
                "To enable auto-updates:\n"
                "1. Clone the repository from GitHub\n"
                "2. Or download updates manually from the releases page"
            )
            self.check_btn.setEnabled(True)
            return

        # Disable buttons during check
        self.check_btn.setEnabled(False)
        self.update_btn.setEnabled(False)

        # Show progress
        self.status_label.setText("🔍 Checking for updates...")
        self.info_text.clear()
        self.progress_bar.show()

        # Start check thread
        self.check_thread = UpdateCheckThread(self.updater)
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.error.connect(self.on_check_error)
        self.check_thread.start()

    def on_check_finished(self, update_info: UpdateInfo):
        """Handle update check finished."""
        self.progress_bar.hide()
        self.check_btn.setEnabled(True)

        if not update_info:
            self.status_label.setText("❌ Failed to check for updates")
            self.info_text.setPlainText("Could not check for updates. Please try again later.")
            return

        self.update_info = update_info

        if update_info.has_updates:
            # Updates available
            self.status_label.setText(
                f"✅ Update available! {update_info.commits_behind} new commit(s)"
            )

            info_text = f"""
<h3>Update Available</h3>

<p><b>Current version:</b> {update_info.current_commit}</p>
<p><b>New version:</b> {update_info.remote_commit}</p>
<p><b>Branch:</b> {update_info.current_branch}</p>
<p><b>Commits behind:</b> {update_info.commits_behind}</p>

<h4>What's new:</h4>
<pre>{update_info.changelog}</pre>

<p>Click "Install Update" to update OctoMaster Pro.</p>
<p><i>Note: Your settings and workflows will be preserved.</i></p>
            """

            self.info_text.setHtml(info_text)
            self.update_btn.setEnabled(True)

        else:
            # Already up to date
            self.status_label.setText("✅ You're up to date!")

            info_text = f"""
<h3>Up to Date</h3>

<p><b>Current version:</b> {update_info.current_commit}</p>
<p><b>Branch:</b> {update_info.current_branch}</p>

<p>You have the latest version of OctoMaster Pro.</p>
            """

            self.info_text.setHtml(info_text)

    def on_check_error(self, error_message: str):
        """Handle update check error."""
        self.progress_bar.hide()
        self.check_btn.setEnabled(True)

        self.status_label.setText("❌ Failed to check for updates")
        self.info_text.setPlainText(f"Error: {error_message}")

    def install_updates(self):
        """Install updates in background thread."""
        if not self.update_info or not self.update_info.has_updates:
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Install Update",
            f"This will update OctoMaster Pro to the latest version.\n\n"
            f"Updates: {self.update_info.commits_behind} new commit(s)\n\n"
            f"Your settings and workflows will be preserved.\n"
            f"The application will need to be restarted after update.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Ask about dependencies
        install_deps = QMessageBox.question(
            self,
            "Update Dependencies",
            "Do you want to update Python dependencies as well?\n\n"
            "This is recommended to ensure all features work correctly.\n"
            "(This may take a few minutes)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

        # Disable buttons during installation
        self.check_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.close_btn.setEnabled(False)

        # Show progress
        self.progress_bar.show()
        self.status_label.setText("⬇️ Installing updates...")

        # Start install thread
        self.install_thread = UpdateInstallThread(self.updater, install_deps)
        self.install_thread.finished.connect(self.on_install_finished)
        self.install_thread.progress.connect(self.on_install_progress)
        self.install_thread.start()

    def on_install_progress(self, message: str):
        """Handle installation progress."""
        self.status_label.setText(message)

    def on_install_finished(self, success: bool, message: str):
        """Handle installation finished."""
        self.progress_bar.hide()
        self.check_btn.setEnabled(True)
        self.close_btn.setEnabled(True)

        if success:
            self.status_label.setText("✅ Update installed successfully!")

            info_text = f"""
<h3>Update Successful</h3>

<p>OctoMaster Pro has been updated successfully!</p>

<pre>{message}</pre>

<p><b>⚠️ Please restart the application to use the new version.</b></p>
            """

            self.info_text.setHtml(info_text)

            QMessageBox.information(
                self,
                "Update Successful",
                "OctoMaster Pro has been updated successfully!\n\n"
                "Please restart the application to use the new version."
            )

            # Close dialog
            self.accept()

        else:
            self.status_label.setText("❌ Update failed")

            info_text = f"""
<h3>Update Failed</h3>

<p>Failed to install update:</p>

<pre>{message}</pre>

<p>You can try again or update manually using Git.</p>
            """

            self.info_text.setHtml(info_text)

            QMessageBox.critical(
                self,
                "Update Failed",
                f"Failed to install update:\n\n{message}"
            )
