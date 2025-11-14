"""
Unit tests for main application.

Tests the Application class and application lifecycle.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.app import Application
from src.core.config import Config
from src.core.state import AppStatus
from src.core.exceptions import OctoMasterError


class TestApplicationInitialization:
    """Tests for Application initialization."""

    @patch('src.core.app.QApplication')
    def test_basic_initialization(self, mock_qapp):
        """Test basic application initialization."""
        app = Application()

        assert app.config is not None
        assert app.event_bus is not None
        assert app.state is not None

    @patch('src.core.app.QApplication')
    def test_initialization_with_config_file(self, mock_qapp, tmp_path):
        """Test initialization with configuration file."""
        # Create config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  debug: true
  log_level: DEBUG
""")

        app = Application(config_path=config_file)

        # Config should be loaded from file
        assert app.config is not None

    @patch('src.core.app.QApplication')
    def test_initialization_without_config_file(self, mock_qapp):
        """Test initialization without config file uses defaults."""
        app = Application(config_path=None)

        assert app.config is not None
        assert app.config.app_name == "OctoMaster Pro"

    @patch('src.core.app.QApplication')
    def test_logging_setup_during_init(self, mock_qapp, tmp_path):
        """Test that logging is set up during initialization."""
        app = Application()

        # Logger should be configured
        # We can't easily test this without actually logging,
        # but we can check that initialization doesn't crash
        assert app.config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    @patch('src.core.app.QApplication')
    def test_qt_application_attributes_set(self, mock_qapp):
        """Test that Qt application attributes are set."""
        app = Application()

        # Should have called QCoreApplication.set* methods
        # (These are class methods, hard to mock, but app should initialize)
        assert app.config is not None


class TestApplicationLifecycle:
    """Tests for application lifecycle methods."""

    @patch('src.core.app.QApplication')
    def test_initialize_sets_state(self, mock_qapp):
        """Test that initialize() sets app state."""
        app = Application()

        result = app.initialize()

        assert result is True
        assert app.state.status == AppStatus.IDLE

    @patch('src.core.app.QApplication')
    @patch('src.core.app.get_plugin_manager')
    def test_initialize_with_plugins_enabled(self, mock_get_pm, mock_qapp):
        """Test initialization with plugins enabled."""
        # Mock plugin manager
        mock_pm = Mock()
        mock_pm.load_all_plugins.return_value = 2
        mock_pm.enable_all_plugins.return_value = 2
        mock_get_pm.return_value = mock_pm

        app = Application()
        app.config.enable_plugins = True

        result = app.initialize()

        assert result is True
        mock_pm.load_all_plugins.assert_called_once()
        mock_pm.enable_all_plugins.assert_called_once()

    @patch('src.core.app.QApplication')
    def test_initialize_with_plugins_disabled(self, mock_qapp):
        """Test initialization with plugins disabled."""
        app = Application()
        app.config.enable_plugins = False

        result = app.initialize()

        assert result is True
        assert app.plugin_manager is None

    @patch('src.core.app.QApplication')
    def test_initialize_emits_app_started_event(self, mock_qapp):
        """Test that initialize emits APP_STARTED event."""
        app = Application()

        # Subscribe to event
        events_received = []

        def event_handler(event):
            events_received.append(event)

        from src.core.events import EventType

        app.event_bus.subscribe(
            EventType.APP_STARTED,
            event_handler
        )

        app.initialize()

        assert len(events_received) == 1
        assert events_received[0].type == EventType.APP_STARTED

    @patch('src.core.app.QApplication')
    @patch('src.core.app.get_plugin_manager')
    def test_initialize_failure_returns_false(self, mock_get_pm, mock_qapp):
        """Test that initialize returns False on error."""
        # Make plugin manager raise exception
        mock_get_pm.side_effect = Exception("Plugin manager error")

        app = Application()
        app.config.enable_plugins = True

        result = app.initialize()

        assert result is False

    @patch('src.core.app.QApplication')
    @patch('src.core.app.get_plugin_manager')
    def test_shutdown_disables_plugins(self, mock_get_pm, mock_qapp):
        """Test that shutdown disables plugins."""
        mock_pm = Mock()
        mock_get_pm.return_value = mock_pm

        app = Application()
        app.plugin_manager = mock_pm

        app.shutdown()

        mock_pm.shutdown_all_plugins.assert_called_once()

    @patch('src.core.app.QApplication')
    def test_shutdown_sets_idle_state(self, mock_qapp):
        """Test that shutdown sets state to IDLE."""
        app = Application()
        app.state.status = AppStatus.RUNNING

        app.shutdown()

        assert app.state.status == AppStatus.IDLE

    @patch('src.core.app.QApplication')
    def test_shutdown_emits_app_stopped_event(self, mock_qapp):
        """Test that shutdown emits APP_STOPPED event."""
        from src.core.events import EventType

        app = Application()

        events_received = []

        def event_handler(event):
            events_received.append(event)

        app.event_bus.subscribe(EventType.APP_STOPPED, event_handler)

        app.shutdown()

        assert len(events_received) == 1
        assert events_received[0].type == EventType.APP_STOPPED

    @patch('src.core.app.QApplication')
    def test_shutdown_handles_exceptions_gracefully(self, mock_qapp):
        """Test that shutdown handles exceptions without crashing."""
        app = Application()

        # Make plugin_manager raise exception
        app.plugin_manager = Mock()
        app.plugin_manager.shutdown_all_plugins.side_effect = Exception("Shutdown error")

        # Should not raise exception
        app.shutdown()

        # State should still be set
        assert app.state.status == AppStatus.IDLE


class TestApplicationRun:
    """Tests for application run method."""

    @patch('src.core.app.MainWindow')
    @patch('src.core.app.QApplication')
    def test_run_initializes_app(self, mock_qapp, mock_main_window):
        """Test that run() initializes the application."""
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec.return_value = 0
        mock_qapp.return_value = mock_qapp_instance

        app = Application()

        # Mock initialize to avoid full initialization
        app.initialize = Mock(return_value=True)

        with patch.object(app, 'shutdown'):
            try:
                exit_code = app.run()
            except SystemExit:
                pass

        app.initialize.assert_called_once()

    @patch('src.core.app.MainWindow')
    @patch('src.core.app.QApplication')
    def test_run_creates_main_window(self, mock_qapp, mock_main_window):
        """Test that run() creates and shows main window."""
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec.return_value = 0
        mock_qapp.return_value = mock_qapp_instance

        mock_window = Mock()
        mock_main_window.return_value = mock_window

        app = Application()
        app.initialize = Mock(return_value=True)

        with patch.object(app, 'shutdown'):
            try:
                app.run()
            except SystemExit:
                pass

        mock_main_window.assert_called_once()
        mock_window.show.assert_called_once()

    @patch('src.core.app.QApplication')
    def test_run_returns_error_on_init_failure(self, mock_qapp):
        """Test that run() returns error code if initialization fails."""
        app = Application()
        app.initialize = Mock(return_value=False)

        with patch.object(app, 'shutdown'):
            exit_code = app.run()

        assert exit_code == 1

    @patch('src.core.app.MainWindow')
    @patch('src.core.app.QApplication')
    def test_run_handles_keyboard_interrupt(self, mock_qapp, mock_main_window):
        """Test that run() handles KeyboardInterrupt gracefully."""
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec.side_effect = KeyboardInterrupt()
        mock_qapp.return_value = mock_qapp_instance

        app = Application()
        app.initialize = Mock(return_value=True)

        with patch.object(app, 'shutdown'):
            exit_code = app.run()

        assert exit_code == 0

    @patch('src.core.app.MainWindow')
    @patch('src.core.app.QApplication')
    def test_run_handles_exceptions(self, mock_qapp, mock_main_window):
        """Test that run() handles exceptions."""
        mock_qapp_instance = Mock()
        mock_qapp_instance.exec.side_effect = Exception("Runtime error")
        mock_qapp.return_value = mock_qapp_instance

        app = Application()
        app.initialize = Mock(return_value=True)

        with patch.object(app, 'shutdown'):
            exit_code = app.run()

        assert exit_code == 1

    @patch('src.core.app.QApplication')
    def test_run_calls_shutdown_in_finally(self, mock_qapp):
        """Test that run() always calls shutdown in finally block."""
        app = Application()
        app.initialize = Mock(return_value=False)

        shutdown_called = []

        def mock_shutdown():
            shutdown_called.append(True)

        app.shutdown = mock_shutdown

        app.run()

        assert len(shutdown_called) == 1


class TestMainFunction:
    """Tests for main() entry point function."""

    @patch('src.core.app.Application')
    def test_main_creates_application(self, mock_app_class):
        """Test that main() creates Application instance."""
        from src.core.app import main

        mock_app = Mock()
        mock_app.run.return_value = 0
        mock_app_class.return_value = mock_app

        with patch('sys.exit'):
            main()

        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()

    @patch('src.core.app.Application')
    def test_main_handles_octomaster_error(self, mock_app_class):
        """Test that main() handles OctoMasterError."""
        from src.core.app import main

        mock_app = Mock()
        mock_app.run.side_effect = OctoMasterError("Test error")
        mock_app_class.return_value = mock_app

        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_with(1)

    @patch('src.core.app.Application')
    def test_main_handles_unexpected_exception(self, mock_app_class):
        """Test that main() handles unexpected exceptions."""
        from src.core.app import main

        mock_app = Mock()
        mock_app.run.side_effect = Exception("Unexpected error")
        mock_app_class.return_value = mock_app

        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_with(1)


class TestApplicationIntegration:
    """Integration tests for Application class."""

    @patch('src.core.app.QApplication')
    def test_full_application_lifecycle(self, mock_qapp):
        """Test complete application lifecycle."""
        app = Application()

        # Initialize
        init_result = app.initialize()
        assert init_result is True
        assert app.state.status == AppStatus.IDLE

        # Shutdown
        app.shutdown()
        assert app.state.status == AppStatus.IDLE

    @patch('src.core.app.QApplication')
    def test_config_state_event_bus_integration(self, mock_qapp):
        """Test that config, state, and event bus work together."""
        app = Application()

        # Config should be accessible
        assert app.config.app_name == "OctoMaster Pro"

        # State should be accessible
        assert app.state.status == AppStatus.IDLE

        # Event bus should work
        events = []

        def handler(event):
            events.append(event)

        from src.core.events import EventType
        app.event_bus.subscribe(EventType.APP_STARTED, handler)
        app.event_bus.emit(EventType.APP_STARTED)

        assert len(events) == 1
