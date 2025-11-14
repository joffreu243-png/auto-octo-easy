"""
Validation utilities for OctoMaster Pro.

This module provides data validation functions.
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_selector(selector: str) -> bool:
    """
    Validate CSS selector format.

    Args:
        selector: CSS selector to validate

    Returns:
        True if valid selector, False otherwise
    """
    if not selector or not isinstance(selector, str):
        return False

    # Basic validation - check for common patterns
    invalid_chars = ["<", ">", "{", "}"]
    return not any(char in selector for char in invalid_chars)


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_cron_expression(expression: str) -> bool:
    """
    Validate cron expression format.

    Args:
        expression: Cron expression to validate

    Returns:
        True if valid cron expression, False otherwise
    """
    # Basic validation - check for 5 fields
    parts = expression.split()
    if len(parts) != 5:
        return False

    # Check each part is valid (number, *, or range)
    for part in parts:
        if part == "*":
            continue
        if "-" in part:
            try:
                start, end = part.split("-")
                int(start)
                int(end)
            except (ValueError, AttributeError):
                return False
        else:
            try:
                int(part)
            except ValueError:
                return False

    return True
