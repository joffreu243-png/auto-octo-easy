"""
Smart tips system for OctoMaster Pro.

Context-aware tips and suggestions for users.
"""

from typing import List, Dict, Any
from loguru import logger


class SmartTips:
    """Context-aware tips for users."""

    def __init__(self):
        """Initialize smart tips."""
        self.tips: Dict[str, List[str]] = {}
        self.shown_tips: set = set()
        self._setup_tips()
        logger.info("SmartTips initialized")

    def _setup_tips(self) -> None:
        """Setup all tips."""
        self.tips = {
            "first_launch": [
                "💡 Tip: Use templates to get started quickly!",
                "💡 Tip: Press Ctrl+R to start recording browser actions",
                "💡 Tip: Check out tutorials in Help menu",
            ],
            "recorder": [
                "💡 Tip: Click slowly - recorder needs time to capture actions",
                "💡 Tip: Use CSS selectors for more reliable automation",
                "💡 Tip: Test your recording before saving",
            ],
            "node_editor": [
                "💡 Tip: Right-click on canvas for quick block insert",
                "💡 Tip: Use loops for repetitive tasks",
                "💡 Tip: Group related blocks for better organization",
            ],
            "scheduler": [
                "💡 Tip: Use CRON expressions for complex schedules",
                "💡 Tip: Enable notifications to know when tasks complete",
                "💡 Tip: Test your workflow before scheduling",
            ],
            "templates": [
                "💡 Tip: Customize template inputs before using",
                "💡 Tip: Save your workflows as templates to reuse",
                "💡 Tip: Rate templates to help others find good ones",
            ],
        }

    def get_tip(self, context: str) -> str:
        """Get random tip for context.

        Args:
            context: Context name

        Returns:
            Tip text
        """
        if context not in self.tips:
            return ""

        import random
        tips = self.tips[context]
        tip = random.choice(tips)

        # Mark as shown
        self.shown_tips.add(tip)

        return tip

    def get_next_unseen_tip(self, context: str) -> str:
        """Get next unseen tip.

        Args:
            context: Context name

        Returns:
            Tip text or empty string
        """
        if context not in self.tips:
            return ""

        for tip in self.tips[context]:
            if tip not in self.shown_tips:
                self.shown_tips.add(tip)
                return tip

        return ""

    def reset_shown(self) -> None:
        """Reset shown tips."""
        self.shown_tips.clear()
