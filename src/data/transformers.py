"""
Data transformers for cleaning and transforming extracted data.
"""

import re
from typing import Optional
from datetime import datetime
from loguru import logger


class DataTransformer:
    """Transform and clean scraped data."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        return text

    @staticmethod
    def extract_numbers(text: str) -> Optional[float]:
        """Extract first number from text.

        Args:
            text: Text containing number

        Returns:
            Extracted number or None
        """
        match = re.search(r'[\d,]+\.?\d*', text)
        if match:
            num_str = match.group().replace(',', '')
            try:
                return float(num_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email from text.

        Args:
            text: Text containing email

        Returns:
            Email address or None
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group() if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number from text.

        Args:
            text: Text containing phone

        Returns:
            Phone number or None
        """
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}-\d{3}-\d{4}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        return None

    @staticmethod
    def parse_date(text: str) -> Optional[str]:
        """Parse date from text.

        Args:
            text: Text containing date

        Returns:
            ISO format date or None
        """
        try:
            from dateutil import parser
            date = parser.parse(text)
            return date.isoformat()
        except:
            return None

    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """Extract URL from text.

        Args:
            text: Text containing URL

        Returns:
            URL or None
        """
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        match = re.search(pattern, text)
        return match.group() if match else None

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Text with irregular whitespace

        Returns:
            Normalized text
        """
        # Replace tabs and newlines with space
        text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        # Remove extra spaces
        text = re.sub(r' +', ' ', text)
        return text.strip()

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text.

        Args:
            text: HTML text

        Returns:
            Plain text
        """
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    @staticmethod
    def extract_integers(text: str) -> list:
        """Extract all integers from text.

        Args:
            text: Text containing numbers

        Returns:
            List of integers
        """
        return [int(x) for x in re.findall(r'\d+', text)]

    @staticmethod
    def capitalize_words(text: str) -> str:
        """Capitalize first letter of each word.

        Args:
            text: Text to capitalize

        Returns:
            Capitalized text
        """
        return text.title()

    @staticmethod
    def remove_special_chars(text: str, keep: str = " ") -> str:
        """Remove special characters from text.

        Args:
            text: Text with special chars
            keep: Characters to keep

        Returns:
            Cleaned text
        """
        pattern = f"[^a-zA-Z0-9{re.escape(keep)}]"
        return re.sub(pattern, '', text)
