"""
Logging configuration for OctoMaster Pro.

This module provides comprehensive logging setup using loguru,
supporting console, file, and rotation logging with customizable formats.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from src.core.exceptions import ConfigurationError


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "100 MB",
    retention: str = "10 days",
    compression: str = "zip",
    colorize: bool = True,
    backtrace: bool = True,
    diagnose: bool = True,
) -> None:
    """
    Setup application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
        rotation: When to rotate log file (e.g., "100 MB", "1 week")
        retention: How long to keep old logs (e.g., "10 days", "1 month")
        compression: Compression format for rotated logs (gz, bz2, xz, lzma, zip)
        colorize: Enable colored console output
        backtrace: Show backtrace on errors
        diagnose: Show variables in backtrace

    Raises:
        ConfigurationError: If log level is invalid
    """
    # Validate log level
    valid_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        raise ConfigurationError(
            f"Invalid log level: {log_level}. Must be one of {valid_levels}"
        )

    # Remove default handler
    logger.remove()

    # Console handler with custom format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level.upper(),
        colorize=colorize,
        backtrace=backtrace,
        diagnose=diagnose,
        enqueue=True,  # Thread-safe logging
    )

    # File handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

        logger.add(
            str(log_file),
            format=file_format,
            level=log_level.upper(),
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=backtrace,
            diagnose=diagnose,
            enqueue=True,
        )

        # Also create a debug log file with all messages
        debug_log_file = log_file.parent / f"{log_file.stem}_debug{log_file.suffix}"
        logger.add(
            str(debug_log_file),
            format=file_format,
            level="DEBUG",
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

        # Create an error-only log file
        error_log_file = log_file.parent / f"{log_file.stem}_error{log_file.suffix}"
        logger.add(
            str(error_log_file),
            format=file_format,
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

    logger.info(f"Logging initialized at {log_level} level")
    if log_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: Optional[str] = None) -> "logger":  # type: ignore
    """
    Get logger instance.

    Args:
        name: Logger name (module name typically)

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_function_call(func_name: str, args: tuple, kwargs: dict) -> None:
    """
    Log function call with arguments.

    Args:
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
    """
    logger.debug(f"Calling {func_name}(args={args}, kwargs={kwargs})")


def log_exception(exc: Exception, context: str = "") -> None:
    """
    Log exception with context.

    Args:
        exc: Exception to log
        context: Additional context information
    """
    context_str = f" [{context}]" if context else ""
    logger.exception(f"Exception occurred{context_str}: {exc}")


def log_workflow_event(
    event_type: str,
    workflow_id: str,
    block_id: Optional[str] = None,
    message: str = "",
) -> None:
    """
    Log workflow execution event.

    Args:
        event_type: Type of event (start, complete, error, etc.)
        workflow_id: Workflow ID
        block_id: Block ID (optional)
        message: Additional message
    """
    block_info = f", block={block_id}" if block_id else ""
    logger.info(f"Workflow {event_type} [workflow={workflow_id}{block_info}] {message}")


def log_browser_event(
    event_type: str,
    url: Optional[str] = None,
    message: str = "",
) -> None:
    """
    Log browser automation event.

    Args:
        event_type: Type of event (navigate, click, type, etc.)
        url: URL (optional)
        message: Additional message
    """
    url_info = f", url={url}" if url else ""
    logger.debug(f"Browser {event_type}{url_info} {message}")


def log_performance(operation: str, duration_ms: float) -> None:
    """
    Log performance metrics.

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
    """
    logger.info(f"Performance: {operation} took {duration_ms:.2f}ms")


# Create module-level logger
_module_logger = logger.bind(name="octomaster.core.logger")


if __name__ == "__main__":
    # Test logging setup
    setup_logger(log_level="DEBUG", log_file=Path("test.log"))
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(e, "Testing exception logging")
