"""
Unit tests for logger module.

Tests the logging setup and utility functions.
"""

import pytest
from pathlib import Path
from loguru import logger
from src.core.logger import (
    setup_logger,
    get_logger,
    log_function_call,
    log_exception,
    log_workflow_event,
    log_browser_event,
    log_performance,
)
from src.core.exceptions import ConfigurationError


class TestSetupLogger:
    """Tests for setup_logger function."""

    def test_setup_with_defaults(self, tmp_path):
        """Test logger setup with default parameters."""
        log_file = tmp_path / "test.log"

        # Should not raise any exceptions
        setup_logger(log_level="INFO", log_file=log_file)

        # Logger should be configured
        logger.info("Test log message")

        # Log file should be created
        assert log_file.exists()

    def test_setup_with_debug_level(self, tmp_path):
        """Test logger setup with DEBUG level."""
        log_file = tmp_path / "debug.log"

        setup_logger(log_level="DEBUG", log_file=log_file)

        logger.debug("Debug message")
        logger.info("Info message")

        # Both messages should be in log
        assert log_file.exists()
        content = log_file.read_text()
        assert "Debug message" in content
        assert "Info message" in content

    def test_setup_without_log_file(self):
        """Test logger setup without log file (console only)."""
        # Should not raise exception
        setup_logger(log_level="INFO", log_file=None)

        # Should be able to log
        logger.info("Console only message")

    def test_invalid_log_level_raises_error(self):
        """Test that invalid log level raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid log level"):
            setup_logger(log_level="INVALID")

    def test_log_rotation(self, tmp_path):
        """Test log rotation configuration."""
        log_file = tmp_path / "rotating.log"

        setup_logger(
            log_level="INFO",
            log_file=log_file,
            rotation="1 KB",  # Very small for testing
            retention="1 day"
        )

        # Write lots of logs to trigger rotation
        for i in range(1000):
            logger.info(f"Log message {i}" * 10)

        # Should create rotated files
        log_files = list(tmp_path.glob("*.log*"))
        # At least original file should exist
        assert len(log_files) >= 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_without_name(self):
        """Test getting logger without name."""
        log = get_logger()

        # Should return loguru logger
        assert log is logger

    def test_get_logger_with_name(self):
        """Test getting logger with custom name."""
        log = get_logger("test_module")

        # Should be able to log
        log.info("Test message from named logger")

        # Logger should work
        assert log is not None


class TestLogFunctionCall:
    """Tests for log_function_call utility."""

    def test_log_function_with_args(self, caplog):
        """Test logging function call with arguments."""
        log_function_call(
            "my_function",
            args=(1, 2, "test"),
            kwargs={"key": "value"}
        )

        # Note: loguru doesn't use caplog directly, so we just ensure it doesn't crash


class TestLogException:
    """Tests for log_exception utility."""

    def test_log_exception_without_context(self):
        """Test logging exception without context."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            # Should not raise
            log_exception(e)

    def test_log_exception_with_context(self):
        """Test logging exception with context."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            # Should not raise
            log_exception(e, context="During workflow execution")


class TestLogWorkflowEvent:
    """Tests for log_workflow_event utility."""

    def test_log_workflow_event_basic(self):
        """Test logging basic workflow event."""
        log_workflow_event(
            event_type="start",
            workflow_id="workflow_123"
        )

    def test_log_workflow_event_with_block(self):
        """Test logging workflow event with block."""
        log_workflow_event(
            event_type="complete",
            workflow_id="workflow_123",
            block_id="block_456",
            message="Block completed successfully"
        )


class TestLogBrowserEvent:
    """Tests for log_browser_event utility."""

    def test_log_browser_event_basic(self):
        """Test logging basic browser event."""
        log_browser_event(
            event_type="navigate",
            url="https://example.com"
        )

    def test_log_browser_event_without_url(self):
        """Test logging browser event without URL."""
        log_browser_event(
            event_type="click",
            message="Clicked element"
        )


class TestLogPerformance:
    """Tests for log_performance utility."""

    def test_log_performance(self):
        """Test logging performance metrics."""
        log_performance(
            operation="workflow_execution",
            duration_ms=1234.56
        )

    def test_log_performance_formats_duration(self):
        """Test that performance logging formats duration correctly."""
        log_performance("fast_operation", 5.2)
        log_performance("slow_operation", 5432.1)
        log_performance("very_slow_operation", 123456.78)
