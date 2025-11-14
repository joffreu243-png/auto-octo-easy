"""
Email notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from loguru import logger


class EmailNotifier:
    """Send email notifications."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str,
                 use_tls: bool = True) -> None:
        """Initialize email notifier.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
            use_tls: Use TLS encryption
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
    
    async def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Send email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            
        Returns:
            True if sent successfully
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_task_notification(self, task, status: str, message: str) -> bool:
        """Send task notification email.
        
        Args:
            task: Task object
            status: Task status
            message: Notification message
            
        Returns:
            True if sent
        """
        subject = f"[OctoMaster Pro] Task '{task.name}' - {status.upper()}"
        
        body = f"""
Task Notification
{'=' * 50}

Task: {task.name}
Status: {status}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Description:
{task.description}

Message:
{message}

Statistics:
- Total runs: {task.run_count}
- Successes: {task.success_count}
- Failures: {task.failure_count}
"""
        
        if task.email_to:
            return await self.send(task.email_to, subject, body)
        
        return False
