"""
Data validators for OctoMaster Pro.
"""

import re
from typing import Any
from loguru import logger

from src.data.types import ValidationResult


class BaseValidator:
    """Base validator class."""

    def validate(self, value: Any) -> ValidationResult:
        """Validate value.

        Args:
            value: Value to validate

        Returns:
            Validation result
        """
        raise NotImplementedError


class EmailValidator(BaseValidator):
    """Validate email addresses."""

    def validate(self, value: str) -> ValidationResult:
        """Validate email.

        Args:
            value: Email string

        Returns:
            Validation result
        """
        if not value:
            return ValidationResult(is_valid=False, errors=["Email is required"])

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(pattern, value):
            return ValidationResult(is_valid=True)
        else:
            return ValidationResult(is_valid=False, errors=["Invalid email format"])


class URLValidator(BaseValidator):
    """Validate URLs."""

    def validate(self, value: str) -> ValidationResult:
        """Validate URL.

        Args:
            value: URL string

        Returns:
            Validation result
        """
        if not value:
            return ValidationResult(is_valid=False, errors=["URL is required"])

        pattern = r'^https?://[^\s/$.?#].[^\s]*$'

        if re.match(pattern, value):
            return ValidationResult(is_valid=True)
        else:
            return ValidationResult(is_valid=False, errors=["Invalid URL format"])


class PhoneValidator(BaseValidator):
    """Validate phone numbers."""

    def validate(self, value: str) -> ValidationResult:
        """Validate phone number.

        Args:
            value: Phone string

        Returns:
            Validation result
        """
        if not value:
            return ValidationResult(is_valid=False, errors=["Phone is required"])

        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', value)

        # Check if it's 10-15 digits
        if re.match(r'^\+?\d{10,15}$', cleaned):
            return ValidationResult(is_valid=True)
        else:
            return ValidationResult(is_valid=False, errors=["Invalid phone format"])


class NumberValidator(BaseValidator):
    """Validate numbers."""

    def __init__(self, min_value: float = None, max_value: float = None):
        """Initialize number validator.

        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        """
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> ValidationResult:
        """Validate number.

        Args:
            value: Number to validate

        Returns:
            Validation result
        """
        try:
            num = float(value)

            if self.min_value is not None and num < self.min_value:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Value must be >= {self.min_value}"]
                )

            if self.max_value is not None and num > self.max_value:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Value must be <= {self.max_value}"]
                )

            return ValidationResult(is_valid=True)

        except (ValueError, TypeError):
            return ValidationResult(is_valid=False, errors=["Invalid number format"])


class RequiredValidator(BaseValidator):
    """Validate required fields."""

    def validate(self, value: Any) -> ValidationResult:
        """Check if value is provided.

        Args:
            value: Value to check

        Returns:
            Validation result
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(is_valid=False, errors=["Field is required"])

        return ValidationResult(is_valid=True)


class LengthValidator(BaseValidator):
    """Validate string length."""

    def __init__(self, min_length: int = None, max_length: int = None):
        """Initialize length validator.

        Args:
            min_length: Minimum length
            max_length: Maximum length
        """
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: str) -> ValidationResult:
        """Validate string length.

        Args:
            value: String to validate

        Returns:
            Validation result
        """
        if not isinstance(value, str):
            return ValidationResult(is_valid=False, errors=["Value must be string"])

        length = len(value)

        if self.min_length and length < self.min_length:
            return ValidationResult(
                is_valid=False,
                errors=[f"Length must be >= {self.min_length}"]
            )

        if self.max_length and length > self.max_length:
            return ValidationResult(
                is_valid=False,
                errors=[f"Length must be <= {self.max_length}"]
            )

        return ValidationResult(is_valid=True)
