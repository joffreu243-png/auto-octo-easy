"""
Onboarding wizard for OctoMaster Pro.

First-time user experience with interactive setup.
"""

from typing import List, Callable, Optional
from loguru import logger


class OnboardingStep:
    """Single onboarding step."""

    def __init__(self, title: str, description: str, action: Optional[Callable] = None):
        self.title = title
        self.description = description
        self.action = action
        self.completed = False


class OnboardingWizard:
    """Interactive onboarding for new users."""

    def __init__(self, gui: Optional[any] = None):
        """Initialize onboarding wizard.

        Args:
            gui: GUI instance
        """
        self.gui = gui
        self.current_step = 0
        self.steps: List[OnboardingStep] = []
        self._setup_steps()
        logger.info("OnboardingWizard initialized")

    def _setup_steps(self) -> None:
        """Setup onboarding steps."""
        self.steps = [
            OnboardingStep(
                "Welcome to OctoMaster Pro",
                "Let's get you started with browser automation",
            ),
            OnboardingStep(
                "Configure Octo Browser",
                "Enter your Octo Browser API key to connect profiles",
            ),
            OnboardingStep(
                "Create First Profile",
                "Create your first browser profile for automation",
            ),
            OnboardingStep(
                "Record Your First Action",
                "Use the recorder to capture browser interactions",
            ),
            OnboardingStep(
                "Build a Workflow",
                "Create a simple automation workflow using node editor",
            ),
            OnboardingStep(
                "Run Your Workflow",
                "Execute your first automation and see it in action",
            ),
            OnboardingStep(
                "Explore Templates",
                "Browse ready-made templates to jumpstart automation",
            ),
            OnboardingStep(
                "Setup Complete!",
                "You're ready to automate! Check out tutorials for more",
            ),
        ]

    def start(self) -> None:
        """Start onboarding process."""
        self.current_step = 0
        self._show_current_step()
        logger.info("Onboarding started")

    def next_step(self) -> bool:
        """Move to next step.

        Returns:
            True if there are more steps
        """
        if self.current_step < len(self.steps) - 1:
            self.steps[self.current_step].completed = True
            self.current_step += 1
            self._show_current_step()
            return True
        return False

    def previous_step(self) -> bool:
        """Move to previous step.

        Returns:
            True if moved back
        """
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()
            return True
        return False

    def skip(self) -> None:
        """Skip onboarding."""
        logger.info("Onboarding skipped")
        if self.gui:
            self.gui.set_config("onboarding_completed", True)

    def _show_current_step(self) -> None:
        """Show current step to user."""
        step = self.steps[self.current_step]
        logger.debug(f"Onboarding step: {step.title}")

        if self.gui:
            self.gui.show_onboarding_step(step.title, step.description)

        # Execute step action
        if step.action:
            step.action()

    def get_progress(self) -> float:
        """Get onboarding progress.

        Returns:
            Progress percentage (0.0 to 1.0)
        """
        completed = sum(1 for step in self.steps if step.completed)
        return completed / len(self.steps)

    def is_completed(self) -> bool:
        """Check if onboarding is completed.

        Returns:
            True if all steps completed
        """
        return all(step.completed for step in self.steps)
