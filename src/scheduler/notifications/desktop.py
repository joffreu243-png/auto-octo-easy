"""
Desktop notifications.
"""

from loguru import logger


class DesktopNotifier:
    """Send desktop notifications."""
    
    async def send(self, title: str, message: str, icon: str = None) -> bool:
        """Send desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon path
            
        Returns:
            True if sent
        """
        try:
            # Try plyer (cross-platform)
            from plyer import notification
            
            notification.notify(
                title=title,
                message=message,
                app_icon=icon,
                timeout=10
            )
            
            logger.info("Desktop notification sent")
            return True
        
        except ImportError:
            logger.warning("plyer not installed, desktop notifications unavailable")
            return False
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False
    
    async def send_task_notification(self, task, status: str, message: str) -> bool:
        """Send task notification to desktop.
        
        Args:
            task: Task object
            status: Task status
            message: Notification message
            
        Returns:
            True if sent
        """
        title = f"Task: {task.name} - {status.upper()}"
        return await self.send(title, message)
