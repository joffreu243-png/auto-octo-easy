"""
Interval trigger helpers.
"""

from typing import List
from datetime import datetime, timedelta
from loguru import logger


class IntervalHelper:
    """Helper for interval-based triggers."""
    
    @staticmethod
    def validate(seconds: int) -> bool:
        """Validate interval seconds.
        
        Args:
            seconds: Interval in seconds
            
        Returns:
            True if valid
        """
        return seconds > 0
    
    @staticmethod
    def get_next_runs(seconds: int, count: int = 5) -> List[datetime]:
        """Get next N execution times.
        
        Args:
            seconds: Interval in seconds
            count: Number of next runs
            
        Returns:
            List of datetime objects
        """
        now = datetime.now()
        return [now + timedelta(seconds=seconds * (i + 1)) for i in range(count)]
    
    @staticmethod
    def describe(seconds: int) -> str:
        """Human-readable description.
        
        Args:
            seconds: Interval in seconds
            
        Returns:
            Description
        """
        if seconds < 60:
            return f"Every {seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"Every {minutes} minute{'s' if minutes > 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"Every {hours} hour{'s' if hours > 1 else ''}"
        else:
            days = seconds // 86400
            return f"Every {days} day{'s' if days > 1 else ''}"
