"""
Action optimizer for recorded workflows.

Optimizes recorded actions by removing duplicates, merging similar actions,
and improving selector quality.
"""

from typing import List, Dict, Any, Optional, Set
from datetime import timedelta
from loguru import logger

from src.recorder.types import RecordedAction, ActionType, Selector


class ActionOptimizer:
    """Optimizes recorded actions."""

    def __init__(self) -> None:
        """Initialize action optimizer."""
        self.merge_input_threshold = 2.0  # seconds
        self.duplicate_time_threshold = 0.5  # seconds
        self.min_wait_time = 0.5  # seconds

    def optimize(self, actions: List[RecordedAction]) -> List[RecordedAction]:
        """Optimize list of recorded actions.

        Args:
            actions: Raw recorded actions

        Returns:
            Optimized actions
        """
        if not actions:
            return []

        optimized = actions.copy()

        # Remove duplicates
        optimized = self._remove_duplicates(optimized)

        # Merge consecutive input actions
        optimized = self._merge_input_actions(optimized)

        # Remove unnecessary waits
        optimized = self._remove_unnecessary_waits(optimized)

        # Improve selectors
        optimized = self._improve_selectors(optimized)

        # Add implicit waits where needed
        optimized = self._add_implicit_waits(optimized)

        logger.info(f"Optimized {len(actions)} actions to {len(optimized)} actions")

        return optimized

    def _remove_duplicates(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Remove duplicate actions occurring close in time.

        Args:
            actions: Actions to optimize

        Returns:
            Actions without duplicates
        """
        if not actions:
            return []

        result = [actions[0]]

        for action in actions[1:]:
            prev = result[-1]

            # Check if duplicate
            if self._is_duplicate(action, prev):
                time_diff = (action.timestamp - prev.timestamp).total_seconds()

                if time_diff < self.duplicate_time_threshold:
                    # Skip this action
                    logger.debug(
                        f"Removed duplicate: {action.type.value} at {action.timestamp}"
                    )
                    continue

            result.append(action)

        return result

    def _is_duplicate(self, action1: RecordedAction, action2: RecordedAction) -> bool:
        """Check if two actions are duplicates.

        Args:
            action1: First action
            action2: Second action

        Returns:
            True if duplicate
        """
        # Same type
        if action1.type != action2.type:
            return False

        # Same selector
        if action1.best_selector and action2.best_selector:
            if action1.best_selector.value != action2.best_selector.value:
                return False
        elif action1.best_selector or action2.best_selector:
            return False

        # Same value (for input actions)
        if action1.value != action2.value:
            return False

        # Same URL (for navigation)
        if action1.url != action2.url:
            return False

        return True

    def _merge_input_actions(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Merge consecutive input actions to same element.

        Args:
            actions: Actions to optimize

        Returns:
            Actions with merged inputs
        """
        if not actions:
            return []

        result = []
        current_input = None
        input_buffer = []

        for action in actions:
            if action.type in [ActionType.TYPE_TEXT, ActionType.FILL]:
                # Check if same element as current buffer
                if input_buffer:
                    prev_action = input_buffer[-1]

                    if (
                        action.best_selector
                        and prev_action.best_selector
                        and action.best_selector.value == prev_action.best_selector.value
                    ):
                        # Same element - check time difference
                        time_diff = (
                            action.timestamp - prev_action.timestamp
                        ).total_seconds()

                        if time_diff < self.merge_input_threshold:
                            # Add to buffer
                            input_buffer.append(action)
                            continue

                # Flush buffer if starting new element or timeout
                if input_buffer:
                    merged = self._merge_input_buffer(input_buffer)
                    result.append(merged)
                    input_buffer = []

                # Start new buffer
                input_buffer = [action]

            else:
                # Non-input action - flush buffer
                if input_buffer:
                    merged = self._merge_input_buffer(input_buffer)
                    result.append(merged)
                    input_buffer = []

                result.append(action)

        # Flush remaining buffer
        if input_buffer:
            merged = self._merge_input_buffer(input_buffer)
            result.append(merged)

        return result

    def _merge_input_buffer(self, actions: List[RecordedAction]) -> RecordedAction:
        """Merge buffered input actions into single action.

        Args:
            actions: Input actions to merge

        Returns:
            Merged action
        """
        if len(actions) == 1:
            return actions[0]

        # Use first action as base
        merged = actions[0]

        # Combine values
        combined_value = "".join([a.value or "" for a in actions])
        merged.value = combined_value

        # Use latest timestamp
        merged.timestamp = actions[-1].timestamp

        logger.debug(f"Merged {len(actions)} input actions into one")

        return merged

    def _remove_unnecessary_waits(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Remove unnecessary wait actions.

        Args:
            actions: Actions to optimize

        Returns:
            Actions without unnecessary waits
        """
        result = []

        for i, action in enumerate(actions):
            if action.type == ActionType.WAIT:
                # Check if wait is too short
                if action.wait_time and action.wait_time < self.min_wait_time:
                    logger.debug(f"Removed short wait: {action.wait_time}s")
                    continue

                # Check if wait before navigation (usually unnecessary)
                if i < len(actions) - 1:
                    next_action = actions[i + 1]
                    if next_action.type == ActionType.NAVIGATE:
                        logger.debug("Removed wait before navigation")
                        continue

            result.append(action)

        return result

    def _improve_selectors(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Improve selector quality for actions.

        Args:
            actions: Actions to optimize

        Returns:
            Actions with improved selectors
        """
        # This would integrate with SelectorGenerator to re-rank selectors
        # For now, just ensure best_selector is set

        for action in actions:
            if action.selectors and not action.best_selector:
                # Pick highest scored selector
                action.best_selector = max(action.selectors, key=lambda s: s.score)

        return actions

    def _add_implicit_waits(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Add implicit wait actions where needed.

        Args:
            actions: Actions to optimize

        Returns:
            Actions with added waits
        """
        result = []
        wait_threshold = 3.0  # seconds

        for i, action in enumerate(actions):
            result.append(action)

            # Check time to next action
            if i < len(actions) - 1:
                next_action = actions[i + 1]
                time_diff = (next_action.timestamp - action.timestamp).total_seconds()

                # If significant delay, add explicit wait
                if time_diff > wait_threshold:
                    # Don't add wait before navigation or existing waits
                    if next_action.type not in [
                        ActionType.NAVIGATE,
                        ActionType.WAIT,
                        ActionType.WAIT_FOR_ELEMENT,
                    ]:
                        wait_action = RecordedAction(
                            type=ActionType.WAIT,
                            timestamp=action.timestamp,
                            wait_time=min(time_diff, 10.0),  # Cap at 10s
                        )
                        result.append(wait_action)

                        logger.debug(f"Added implicit wait: {time_diff:.1f}s")

        return result

    def deduplicate_selectors(self, actions: List[RecordedAction]) -> List[RecordedAction]:
        """Remove duplicate selectors from actions.

        Args:
            actions: Actions to process

        Returns:
            Actions with deduplicated selectors
        """
        for action in actions:
            if len(action.selectors) > 1:
                # Keep only unique selectors
                seen: Set[str] = set()
                unique_selectors = []

                for selector in action.selectors:
                    key = f"{selector.type.value}:{selector.value}"
                    if key not in seen:
                        seen.add(key)
                        unique_selectors.append(selector)

                action.selectors = unique_selectors

        return actions

    def optimize_selector_list(
        self, actions: List[RecordedAction], max_selectors: int = 3
    ) -> List[RecordedAction]:
        """Limit number of selectors per action.

        Args:
            actions: Actions to process
            max_selectors: Maximum selectors to keep per action

        Returns:
            Actions with limited selectors
        """
        for action in actions:
            if len(action.selectors) > max_selectors:
                # Keep top N selectors by score
                action.selectors = sorted(
                    action.selectors, key=lambda s: s.score, reverse=True
                )[:max_selectors]

        return actions

    def remove_navigation_duplicates(
        self, actions: List[RecordedAction]
    ) -> List[RecordedAction]:
        """Remove duplicate navigation to same URL.

        Args:
            actions: Actions to process

        Returns:
            Actions without duplicate navigations
        """
        result = []
        last_url = None

        for action in actions:
            if action.type == ActionType.NAVIGATE:
                if action.url == last_url:
                    logger.debug(f"Removed duplicate navigation to: {action.url}")
                    continue

                last_url = action.url

            result.append(action)

        return result
