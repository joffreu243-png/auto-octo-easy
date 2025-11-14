#!/usr/bin/env python3
"""
Test GUI application for OctoMaster Pro.

Simple test application to verify GUI components work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main() -> int:
    """Run test GUI application.

    Returns:
        Exit code
    """
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("OctoMaster Pro")
    app.setOrganizationName("OctoMaster")
    app.setOrganizationDomain("octomaster-pro.com")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
