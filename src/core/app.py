"""
Main application module for OctoMaster Pro.

This module provides the main Application class that initializes and manages
the entire application lifecycle.
"""

import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from loguru import logger

from src.core.config import Config, get_config, set_config
from src.core.logger import setup_logger
from src.core.events import EventBus, EventType, get_event_bus, emit_event
from src.core.state import AppState, get_app_state, AppStatus
from src.core.plugin_manager import PluginManager, get_plugin_manager
from src.core.exceptions import OctoMasterError


class Application:
    """
    Main application class for OctoMaster Pro.

    Manages application lifecycle, initialization, and cleanup.
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize application.

        Args:
            config_path: Path to configuration file (optional)
        """
        # Load configuration
        if config_path and config_path.exists():
            self.config = Config.from_file(config_path)
        else:
            self.config = Config()
        set_config(self.config)

        # Setup logging
        log_file = self.config.logs_dir / "octomaster.log" if self.config.logs_dir else None
        setup_logger(
            log_level=self.config.log_level,
            log_file=log_file,
            colorize=True,
        )

        logger.info("=" * 70)
        logger.info(f"Starting {self.config.app_name} v{self.config.app_version}")
        logger.info("=" * 70)

        # Initialize core components
        self.event_bus = get_event_bus()
        self.state = get_app_state()
        self.plugin_manager: Optional[PluginManager] = None

        # Qt Application
        self.qt_app: Optional[QApplication] = None
        self.main_window: Optional[Any] = None  # Will be GUI MainWindow

        # Setup Qt application attributes
        QCoreApplication.setOrganizationName("OctoMaster")
        QCoreApplication.setOrganizationDomain("octomaster.pro")
        QCoreApplication.setApplicationName("OctoMaster Pro")
        QCoreApplication.setApplicationVersion(self.config.app_version)

    def initialize(self) -> bool:
        """
        Initialize application components.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing application components...")

            # Initialize Qt Application
            self.qt_app = QApplication(sys.argv)
            self.qt_app.setStyle("Fusion")  # Modern cross-platform style

            # Set Qt attributes for better performance
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

            # Initialize plugin manager if enabled
            if self.config.enable_plugins:
                logger.info("Initializing plugin system...")
                self.plugin_manager = get_plugin_manager(self.config.plugins_dir)
                loaded_count = self.plugin_manager.load_all_plugins()
                logger.info(f"Loaded {loaded_count} plugins")

                # Enable plugins
                enabled_count = self.plugin_manager.enable_all_plugins()
                logger.info(f"Enabled {enabled_count} plugins")

            # Initialize database
            logger.info("Initializing database...")
            # TODO: Initialize database connection and create tables

            # Initialize scheduler if enabled
            if self.config.enable_scheduler:
                logger.info("Initializing scheduler...")
                # TODO: Initialize scheduler

            # Update state
            self.state.status = AppStatus.IDLE

            # Emit application started event
            emit_event(EventType.APP_STARTED, {
                "version": self.config.app_version,
                "debug": self.config.debug,
            })

            logger.info("Application initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            emit_event(EventType.APP_ERROR, {"error": str(e)})
            return False

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code
        """
        try:
            if not self.initialize():
                logger.error("Initialization failed, exiting...")
                return 1

            logger.info("Starting GUI...")

            # Create and show main window
            from src.gui.main_window import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()

            # Update state
            self.state.status = AppStatus.RUNNING

            logger.info("Application running. Press Ctrl+C or close window to exit.")

            # Run Qt event loop
            if self.qt_app:
                exit_code = self.qt_app.exec()
            else:
                exit_code = 1

            logger.info(f"Application exiting with code {exit_code}")
            return exit_code

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            return 0

        except Exception as e:
            logger.error(f"Application error: {e}")
            logger.exception(e)
            emit_event(EventType.APP_ERROR, {"error": str(e)})
            return 1

        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown application and cleanup resources."""
        logger.info("Shutting down application...")

        try:
            # Shutdown plugins
            if self.plugin_manager:
                logger.info("Shutting down plugins...")
                self.plugin_manager.shutdown_all_plugins()

            # Update state
            self.state.status = AppStatus.IDLE

            # Emit application stopped event
            emit_event(EventType.APP_STOPPED, {
                "uptime_seconds": self.state.uptime_seconds
            })

            logger.info("Application shutdown complete")
            logger.info(f"Total uptime: {self.state.uptime_seconds:.2f} seconds")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def restart(self) -> None:
        """Restart the application."""
        logger.info("Restarting application...")
        self.shutdown()
        # TODO: Implement restart logic
        logger.info("Please restart the application manually")


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code
    """
    try:
        # Parse command line arguments
        # TODO: Add argument parser for CLI options

        # Create and run application
        app = Application()
        return app.run()

    except OctoMasterError as e:
        logger.error(f"OctoMaster error: {e}")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
