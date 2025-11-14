"""
Utility helpers for OctoMaster Pro.

Provides common utility functions for workflows and automation.
"""

import re
import time
import asyncio
import hashlib
from typing import Any, Callable, Optional, TypeVar, Union, List
from functools import wraps
from pathlib import Path
from datetime import datetime, timedelta
import json

from loguru import logger


T = TypeVar("T")


# ========== Retry Decorator ==========


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry decorator for functions.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch

    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def flaky_function():
            # May fail occasionally
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")

            raise last_exception

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Async retry decorator.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")

            raise last_exception

        return wrapper

    return decorator


# ========== Timeout Decorator ==========


def timeout(seconds: float):
    """
    Timeout decorator (for sync functions).

    Args:
        seconds: Timeout in seconds

    Raises:
        TimeoutError: If function exceeds timeout
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def handler(signum, frame):
                raise TimeoutError(f"Function exceeded timeout of {seconds}s")

            # Set alarm
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Cancel alarm

            return result

        return wrapper

    return decorator


# ========== Selector Helpers ==========


class SelectorBuilder:
    """Build CSS selectors programmatically."""

    @staticmethod
    def by_id(element_id: str) -> str:
        """Build selector by ID."""
        return f"#{element_id}"

    @staticmethod
    def by_class(class_name: str) -> str:
        """Build selector by class."""
        return f".{class_name}"

    @staticmethod
    def by_tag(tag_name: str) -> str:
        """Build selector by tag."""
        return tag_name

    @staticmethod
    def by_attribute(attribute: str, value: str) -> str:
        """Build selector by attribute."""
        return f"[{attribute}='{value}']"

    @staticmethod
    def by_text(text: str, tag: str = "*") -> str:
        """Build XPath selector by text content."""
        return f"//{tag}[contains(text(), '{text}')]"

    @staticmethod
    def combine(*selectors: str, combinator: str = " ") -> str:
        """
        Combine multiple selectors.

        Args:
            *selectors: Selectors to combine
            combinator: Combinator (' ', '>', '+', '~')

        Returns:
            Combined selector
        """
        return combinator.join(selectors)

    @staticmethod
    def nth_child(selector: str, n: int) -> str:
        """Get nth child."""
        return f"{selector}:nth-child({n})"

    @staticmethod
    def first_child(selector: str) -> str:
        """Get first child."""
        return f"{selector}:first-child"

    @staticmethod
    def last_child(selector: str) -> str:
        """Get last child."""
        return f"{selector}:last-child"


def is_valid_selector(selector: str) -> bool:
    """
    Check if a CSS selector is valid.

    Args:
        selector: CSS selector

    Returns:
        True if valid
    """
    try:
        # Basic validation - check for common patterns
        if not selector or not selector.strip():
            return False

        # Check for balanced brackets
        if selector.count("[") != selector.count("]"):
            return False

        if selector.count("(") != selector.count(")"):
            return False

        return True
    except Exception:
        return False


# ========== Data Validators ==========


class Validators:
    """Common validation functions."""

    @staticmethod
    def is_url(url: str) -> bool:
        """Validate URL."""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(url))

    @staticmethod
    def is_email(email: str) -> bool:
        """Validate email address."""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(email_pattern.match(email))

    @staticmethod
    def is_phone(phone: str) -> bool:
        """Validate phone number."""
        # Remove common separators
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        # Check if remaining is digits with optional + prefix
        return bool(re.match(r"^\+?\d{10,15}$", cleaned))

    @staticmethod
    def is_json(text: str) -> bool:
        """Validate JSON string."""
        try:
            json.loads(text)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """Validate IPv4 address."""
        parts = ip.split(".")
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False


# ========== String Helpers ==========


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)

    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9\-]", "", text)

    # Remove consecutive hyphens
    text = re.sub(r"-+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    return text


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from text.

    Args:
        text: Text to extract from

    Returns:
        List of numbers
    """
    pattern = r"-?\d+\.?\d*"
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]


# ========== File Helpers ==========


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """
    Get file hash.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hex digest of file hash
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def get_file_size_readable(file_path: Union[str, Path]) -> str:
    """
    Get human-readable file size.

    Args:
        file_path: Path to file

    Returns:
        Formatted file size (e.g., "1.5 MB")
    """
    size = Path(file_path).stat().st_size

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

    return f"{size:.2f} PB"


# ========== Time Helpers ==========


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration (e.g., "1h 23m 45s")
    """
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m"


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds.

    Args:
        duration_str: Duration string (e.g., "1h30m", "90s", "1.5h")

    Returns:
        Duration in seconds
    """
    # Pattern: number followed by unit (h, m, s)
    pattern = r"(\d+(?:\.\d+)?)\s*([hms])"
    matches = re.findall(pattern, duration_str.lower())

    total_seconds = 0.0

    for value, unit in matches:
        value = float(value)

        if unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value

    return total_seconds


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp string.

    Args:
        format: strftime format string

    Returns:
        Formatted timestamp
    """
    return datetime.now().strftime(format)


# ========== Variable Substitution ==========


def substitute_variables(text: str, variables: dict) -> str:
    """
    Substitute {{variable}} placeholders in text.

    Args:
        text: Text with placeholders
        variables: Dictionary of variable values

    Returns:
        Text with substituted values
    """
    if not isinstance(text, str):
        return text

    # Find all {{variable}} patterns
    pattern = r"\{\{(\w+)\}\}"

    def replacer(match):
        var_name = match.group(1)
        return str(variables.get(var_name, match.group(0)))

    return re.sub(pattern, replacer, text)


def extract_variables(text: str) -> List[str]:
    """
    Extract variable names from {{variable}} placeholders.

    Args:
        text: Text with placeholders

    Returns:
        List of variable names
    """
    pattern = r"\{\{(\w+)\}\}"
    return re.findall(pattern, text)


# ========== Color Helpers ==========


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB.

    Args:
        hex_color: Hex color (e.g., "#FF5733" or "FF5733")

    Returns:
        RGB tuple (r, g, b)
    """
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB to hex color.

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        Hex color string
    """
    return f"#{r:02x}{g:02x}{b:02x}"


# ========== JSON Helpers ==========


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON with default fallback.

    Args:
        json_str: JSON string
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (ValueError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely dump object to JSON with default fallback.

    Args:
        obj: Object to serialize
        default: Default value if serialization fails

    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, indent=2)
    except (ValueError, TypeError):
        return default
