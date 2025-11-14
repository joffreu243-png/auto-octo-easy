"""
Unit tests for custom exceptions.

Tests all custom exception classes and their behavior.
"""

import pytest
from src.core.exceptions import (
    OctoMasterError,
    ConfigurationError,
    WorkflowError,
    BrowserError,
    PluginError,
    RecorderError,
    AIError,
    SchedulerError,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    NetworkError,
    TimeoutError,
)


class TestOctoMasterError:
    """Tests for base OctoMasterError exception."""

    def test_basic_creation(self):
        """Test creating basic error with message."""
        error = OctoMasterError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}

    def test_with_details(self):
        """Test creating error with additional details."""
        error = OctoMasterError(
            "Error occurred",
            details={"code": 500, "reason": "Internal error"}
        )

        assert error.message == "Error occurred"
        assert error.details["code"] == 500
        assert error.details["reason"] == "Internal error"

    def test_string_representation_with_details(self):
        """Test string representation includes details."""
        error = OctoMasterError(
            "Error",
            details={"key": "value", "number": 42}
        )

        error_str = str(error)
        assert "Error" in error_str
        assert "key=value" in error_str
        assert "number=42" in error_str


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_inherits_from_base(self):
        """Test that ConfigurationError inherits from OctoMasterError."""
        error = ConfigurationError("Config error")

        assert isinstance(error, OctoMasterError)
        assert isinstance(error, ConfigurationError)

    def test_error_message(self):
        """Test configuration error message."""
        error = ConfigurationError("Invalid configuration file")

        assert str(error) == "Invalid configuration file"


class TestWorkflowError:
    """Tests for WorkflowError."""

    def test_basic_workflow_error(self):
        """Test basic workflow error."""
        error = WorkflowError("Workflow execution failed")

        assert str(error) == "Workflow execution failed"
        assert error.workflow_id is None
        assert error.block_id is None

    def test_with_workflow_id(self):
        """Test workflow error with workflow_id."""
        error = WorkflowError(
            "Execution failed",
            workflow_id="workflow_123"
        )

        assert error.workflow_id == "workflow_123"
        assert "workflow_id=workflow_123" in str(error)

    def test_with_block_id(self):
        """Test workflow error with block_id."""
        error = WorkflowError(
            "Block execution failed",
            workflow_id="workflow_123",
            block_id="block_456"
        )

        assert error.workflow_id == "workflow_123"
        assert error.block_id == "block_456"
        assert "workflow_id=workflow_123" in str(error)
        assert "block_id=block_456" in str(error)

    def test_with_additional_details(self):
        """Test workflow error with additional details."""
        error = WorkflowError(
            "Error",
            workflow_id="wf_1",
            block_id="block_1",
            details={"attempt": 3, "timeout": True}
        )

        assert error.details["workflow_id"] == "wf_1"
        assert error.details["block_id"] == "block_1"
        assert error.details["attempt"] == 3
        assert error.details["timeout"] is True


class TestBrowserError:
    """Tests for BrowserError."""

    def test_basic_browser_error(self):
        """Test basic browser error."""
        error = BrowserError("Browser crashed")

        assert str(error) == "Browser crashed"
        assert error.browser_type is None

    def test_with_browser_type(self):
        """Test browser error with type."""
        error = BrowserError(
            "Navigation failed",
            browser_type="playwright"
        )

        assert error.browser_type == "playwright"
        assert "browser_type=playwright" in str(error)


class TestPluginError:
    """Tests for PluginError."""

    def test_basic_plugin_error(self):
        """Test basic plugin error."""
        error = PluginError("Plugin initialization failed")

        assert str(error) == "Plugin initialization failed"
        assert error.plugin_name is None

    def test_with_plugin_name(self):
        """Test plugin error with name."""
        error = PluginError(
            "Failed to load",
            plugin_name="my_custom_plugin"
        )

        assert error.plugin_name == "my_custom_plugin"
        assert "plugin_name=my_custom_plugin" in str(error)


class TestAIError:
    """Tests for AIError."""

    def test_basic_ai_error(self):
        """Test basic AI error."""
        error = AIError("AI request failed")

        assert str(error) == "AI request failed"
        assert error.provider is None

    def test_with_provider(self):
        """Test AI error with provider."""
        error = AIError(
            "API key invalid",
            provider="openai"
        )

        assert error.provider == "openai"
        assert "provider=openai" in str(error)


class TestValidationError:
    """Tests for ValidationError."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Validation failed")

        assert str(error) == "Validation failed"
        assert error.field is None
        assert error.value is None

    def test_with_field_and_value(self):
        """Test validation error with field and value."""
        error = ValidationError(
            "Invalid email",
            field="email",
            value="invalid-email"
        )

        assert error.field == "email"
        assert error.value == "invalid-email"
        assert "field=email" in str(error)
        assert "value=invalid-email" in str(error)


class TestNetworkError:
    """Tests for NetworkError."""

    def test_basic_network_error(self):
        """Test basic network error."""
        error = NetworkError("Connection failed")

        assert str(error) == "Connection failed"
        assert error.url is None
        assert error.status_code is None

    def test_with_url_and_status(self):
        """Test network error with URL and status code."""
        error = NetworkError(
            "Request failed",
            url="https://example.com",
            status_code=404
        )

        assert error.url == "https://example.com"
        assert error.status_code == 404
        assert "url=https://example.com" in str(error)
        assert "status_code=404" in str(error)


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_basic_timeout_error(self):
        """Test basic timeout error."""
        error = TimeoutError("Operation timed out")

        assert str(error) == "Operation timed out"
        assert error.timeout_seconds is None

    def test_with_timeout_duration(self):
        """Test timeout error with duration."""
        error = TimeoutError(
            "Operation timed out",
            timeout_seconds=30.0
        )

        assert error.timeout_seconds == 30.0
        assert "timeout_seconds=30.0" in str(error)


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from OctoMasterError."""
        exceptions = [
            ConfigurationError("test"),
            WorkflowError("test"),
            BrowserError("test"),
            PluginError("test"),
            RecorderError("test"),
            AIError("test"),
            SchedulerError("test"),
            DatabaseError("test"),
            ValidationError("test"),
            AuthenticationError("test"),
            NetworkError("test"),
            TimeoutError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, OctoMasterError)
            assert isinstance(exc, Exception)

    def test_can_catch_as_base_exception(self):
        """Test that specific exceptions can be caught as base exception."""
        try:
            raise WorkflowError("Test error")
        except OctoMasterError as e:
            assert isinstance(e, WorkflowError)
            assert str(e) == "Test error"
        except Exception:
            pytest.fail("Should have been caught as OctoMasterError")
