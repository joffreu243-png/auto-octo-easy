"""
Telegram notifications.
"""

import httpx
from datetime import datetime
from typing import Optional
from loguru import logger


class TelegramNotifier:
    """Send Telegram notifications."""
    
    def __init__(self, bot_token: str) -> None:
        """Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token
        """
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Parse mode (HTML, Markdown)
            
        Returns:
            True if sent
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        'chat_id': chat_id,
                        'text': text,
                        'parse_mode': parse_mode
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram message sent to {chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_task_notification(self, task, status: str, message: str) -> bool:
        """Send task notification via Telegram.
        
        Args:
            task: Task object
            status: Task status
            message: Notification message
            
        Returns:
            True if sent
        """
        status_emoji = {
            'success': '✅',
            'failed': '❌',
            'running': '▶️',
            'paused': '⏸️'
        }.get(status.lower(), '📋')
        
        text = f"""
{status_emoji} <b>Task: {task.name}</b>

<b>Status:</b> {status}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>Description:</b>
{task.description or 'N/A'}

<b>Message:</b>
{message}

<b>Statistics:</b>
• Total runs: {task.run_count}
• Successes: {task.success_count}
• Failures: {task.failure_count}
"""
        
        if task.telegram_chat_id:
            return await self.send_message(task.telegram_chat_id, text)
        
        return False
