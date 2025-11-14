#!/usr/bin/env python3
"""
OctoMaster Pro - Main Entry Point

This is the main entry point for the OctoMaster Pro application.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from loguru import logger
from dotenv import load_dotenv

from octomaster.gui.main_window import MainWindow
from octomaster.core.config import Config


def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Add file handler
    logger.add(
        "logs/octomaster_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("OctoMaster Pro starting...")


def setup_environment():
    """Load environment variables and configure the application."""
    # Load .env file
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        logger.warning(f"No .env file found at {env_file}")

    # Create necessary directories
    directories = ["logs", "screenshots", "downloads", "projects", "temp"]
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)

    logger.info("Environment setup complete")


def main():
    """Main application entry point."""
    # Setup
    setup_logging()
    setup_environment()

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("OctoMaster Pro")
    app.setApplicationVersion("0.1.0-alpha")
    app.setOrganizationName("OctoMaster")
    app.setOrganizationDomain("octomaster.pro")

    # Set app-wide settings
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Load configuration
    config = Config()

    # Create and show main window
    logger.info("Creating main window...")
    main_window = MainWindow(config)
    main_window.show()

    logger.info("OctoMaster Pro is ready!")
    logger.info("=" * 60)

    # Run application
    exit_code = app.exec()

    logger.info("OctoMaster Pro shutting down...")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
