"""
CRON trigger helpers.
"""

from typing import List
from datetime import datetime
from loguru import logger


class CronHelper:
    """Helper for CRON expressions."""
    
    @staticmethod
    def validate(cron_expression: str) -> bool:
        """Validate CRON expression.
        
        Args:
            cron_expression: CRON expression string
            
        Returns:
            True if valid
        """
        try:
            from croniter import croniter
            croniter(cron_expression)
            return True
        except:
            return False
    
    @staticmethod
    def get_next_runs(cron_expression: str, count: int = 5) -> List[datetime]:
        """Get next N execution times.
        
        Args:
            cron_expression: CRON expression
            count: Number of next runs to get
            
        Returns:
            List of datetime objects
        """
        try:
            from croniter import croniter
            cron = croniter(cron_expression, datetime.now())
            return [cron.get_next(datetime) for _ in range(count)]
        except Exception as e:
            logger.error(f"Failed to get next runs: {e}")
            return []
    
    @staticmethod
    def describe(cron_expression: str) -> str:
        """Human-readable description of CRON.
        
        Args:
            cron_expression: CRON expression
            
        Returns:
            Human-readable description
        """
        try:
            from cron_descriptor import get_description
            return get_description(cron_expression)
        except:
            # Fallback to simple description
            parts = cron_expression.split()
            if len(parts) >= 5:
                minute, hour, day, month, weekday = parts[:5]
                
                if minute == '*' and hour == '*':
                    return "Every minute"
                elif minute != '*' and hour == '*':
                    return f"Every hour at minute {minute}"
                elif hour != '*' and minute != '*':
                    return f"Every day at {hour}:{minute}"
            
            return cron_expression
