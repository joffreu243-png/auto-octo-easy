"""
Interactive tutorials for OctoMaster Pro.

In-app tutorials with UI highlighting and guidance.
"""

from typing import List, Dict, Any, Optional
from loguru import logger


class TutorialStep:
    """Single tutorial step with UI highlighting."""

    def __init__(self, element: str, title: str, text: str, highlight: bool = True):
        self.element = element  # CSS selector or element ID
        self.title = title
        self.text = text
        self.highlight = highlight


class InteractiveTutorial:
    """Interactive in-app tutorials."""

    def __init__(self, gui: Optional[any] = None):
        """Initialize tutorials.

        Args:
            gui: GUI instance
        """
        self.gui = gui
        self.tutorials: Dict[str, List[TutorialStep]] = {}
        self._setup_tutorials()
        logger.info("InteractiveTutorial initialized")

    def _setup_tutorials(self) -> None:
        """Setup all tutorials."""
        # Recorder tutorial
        self.tutorials["recorder"] = [
            TutorialStep(
                "#record-button",
                "Start Recording",
                "Click here to start recording your browser actions",
                highlight=True,
            ),
            TutorialStep(
                "#browser-view",
                "Perform Actions",
                "Now perform actions in the browser. Each action will be recorded automatically.",
                highlight=True,
            ),
            TutorialStep(
                "#stop-button",
                "Stop Recording",
                "When finished, click stop to end recording",
                highlight=True,
            ),
            TutorialStep(
                "#recorded-actions",
                "Review Actions",
                "Review the recorded actions here. You can edit or remove them.",
                highlight=True,
            ),
        ]

        # Node editor tutorial
        self.tutorials["node_editor"] = [
            TutorialStep(
                "#block-palette",
                "Block Palette",
                "Drag blocks from here to build your workflow",
                highlight=True,
            ),
            TutorialStep(
                "#canvas",
                "Workflow Canvas",
                "Drop blocks here and connect them to create automation",
                highlight=True,
            ),
            TutorialStep(
                "#execute-button",
                "Execute Workflow",
                "Click here to run your workflow and see it in action",
                highlight=True,
            ),
        ]

        # Scheduler tutorial
        self.tutorials["scheduler"] = [
            TutorialStep(
                "#new-task-button",
                "Create Task",
                "Click here to create a new scheduled task",
                highlight=True,
            ),
            TutorialStep(
                "#trigger-settings",
                "Set Schedule",
                "Configure when your task should run (cron, interval, or specific time)",
                highlight=True,
            ),
            TutorialStep(
                "#save-task",
                "Save Task",
                "Save your task - it will run automatically on schedule",
                highlight=True,
            ),
        ]

    def start_tutorial(self, tutorial_name: str) -> bool:
        """Start specific tutorial.

        Args:
            tutorial_name: Tutorial name

        Returns:
            True if tutorial exists
        """
        if tutorial_name not in self.tutorials:
            logger.warning(f"Tutorial not found: {tutorial_name}")
            return False

        steps = self.tutorials[tutorial_name]
        self._show_steps(steps)
        logger.info(f"Started tutorial: {tutorial_name}")
        return True

    def _show_steps(self, steps: List[TutorialStep]) -> None:
        """Show tutorial steps with UI highlighting.

        Args:
            steps: Tutorial steps
        """
        for step in steps:
            if self.gui:
                self.gui.show_tutorial_step(step)

    def get_available_tutorials(self) -> List[str]:
        """Get list of available tutorials.

        Returns:
            Tutorial names
        """
        return list(self.tutorials.keys())
