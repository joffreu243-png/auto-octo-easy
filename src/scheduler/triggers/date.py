"""
Date/time trigger helpers.
"""

from datetime import datetime
from loguru import logger


class DateHelper:
    """Helper for date/time triggers."""
    
    @staticmethod
    def validate(run_date: datetime) -> bool:
        """Validate run date.
        
        Args:
            run_date: Date/time to run
            
        Returns:
            True if valid (in future)
        """
        return run_date > datetime.now()
    
    @staticmethod
    def describe(run_date: datetime) -> str:
        """Human-readable description.
        
        Args:
            run_date: Date/time to run
            
        Returns:
            Description
        """
        now = datetime.now()
        delta = run_date - now
        
        if delta.days > 0:
            return f"On {run_date.strftime('%Y-%m-%d at %H:%M')}"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"In {hours} hour{'s' if hours > 1 else ''}"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"In {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return f"In {delta.seconds} seconds"
