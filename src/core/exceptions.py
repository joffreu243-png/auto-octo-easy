"""
Custom exceptions for OctoMaster Pro.

This module defines all custom exceptions used throughout the application,
providing clear error hierarchies and detailed error messages.
"""

from typing import Any, Optional


class OctoMasterError(Exception):
    """Base exception for all OctoMaster Pro errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize OctoMaster error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(OctoMasterError):
    """Raised when there's a configuration error."""

    pass


class WorkflowError(OctoMasterError):
    """Raised when there's an error in workflow execution or validation."""

    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        block_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize workflow error.

        Args:
            message: Error message
            workflow_id: ID of the workflow that caused the error
            block_id: ID of the block that caused the error
            details: Additional error details
        """
        error_details = details or {}
        if workflow_id:
            error_details["workflow_id"] = workflow_id
        if block_id:
            error_details["block_id"] = block_id
        super().__init__(message, error_details)
        self.workflow_id = workflow_id
        self.block_id = block_id


class BrowserError(OctoMasterError):
    """Raised when there's an error with browser automation."""

    def __init__(
        self,
        message: str,
        browser_type: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize browser error.

        Args:
            message: Error message
            browser_type: Type of browser (playwright, selenium, webengine)
            details: Additional error details
        """
        error_details = details or {}
        if browser_type:
            error_details["browser_type"] = browser_type
        super().__init__(message, error_details)
        self.browser_type = browser_type


class PluginError(OctoMasterError):
    """Raised when there's an error with plugins."""

    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize plugin error.

        Args:
            message: Error message
            plugin_name: Name of the plugin that caused the error
            details: Additional error details
        """
        error_details = details or {}
        if plugin_name:
            error_details["plugin_name"] = plugin_name
        super().__init__(message, error_details)
        self.plugin_name = plugin_name


class RecorderError(OctoMasterError):
    """Raised when there's an error with recording actions."""

    pass


class AIError(OctoMasterError):
    """Raised when there's an error with AI assistant."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize AI error.

        Args:
            message: Error message
            provider: AI provider (openai, anthropic, etc.)
            details: Additional error details
        """
        error_details = details or {}
        if provider:
            error_details["provider"] = provider
        super().__init__(message, error_details)
        self.provider = provider


class SchedulerError(OctoMasterError):
    """Raised when there's an error with task scheduling."""

    pass


class DatabaseError(OctoMasterError):
    """Raised when there's a database error."""

    pass


class ValidationError(OctoMasterError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)
        super().__init__(message, error_details)
        self.field = field
        self.value = value


class AuthenticationError(OctoMasterError):
    """Raised when authentication fails."""

    pass


class NetworkError(OctoMasterError):
    """Raised when there's a network error."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize network error.

        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code
            details: Additional error details
        """
        error_details = details or {}
        if url:
            error_details["url"] = url
        if status_code:
            error_details["status_code"] = status_code
        super().__init__(message, error_details)
        self.url = url
        self.status_code = status_code


class TimeoutError(OctoMasterError):
    """Raised when an operation times out."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize timeout error.

        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
            details: Additional error details
        """
        error_details = details or {}
        if timeout_seconds:
            error_details["timeout_seconds"] = timeout_seconds
        super().__init__(message, error_details)
        self.timeout_seconds = timeout_seconds
