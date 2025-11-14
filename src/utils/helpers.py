"""
Helper utilities for OctoMaster Pro.

This module provides common utility functions.
"""

import time
from uuid import uuid4
from typing import Callable, Any, TypeVar
from functools import wraps
from loguru import logger


T = TypeVar('T')


def generate_id() -> str:
    """
    Generate unique ID.

    Returns:
        Unique identifier string
    """
    return str(uuid4())


def format_duration(milliseconds: float) -> str:
    """
    Format duration in milliseconds to human-readable string.

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        Formatted duration string
    """
    seconds = milliseconds / 1000

    if seconds < 1:
        return f"{milliseconds:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator for functions.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Backoff multiplier for delay

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")

            raise last_exception  # type: ignore

        return wrapper

    return decorator
