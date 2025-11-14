"""
Action analyzer for detecting patterns in recorded actions.

Detects loops, conditions, and optimizes action sequences.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta
from loguru import logger

from src.recorder.types import (
    RecordedAction,
    ActionType,
    ActionPattern,
    OptimizedAction,
)


class ActionAnalyzer:
    """Analyzes recorded actions to detect patterns and optimize."""

    def __init__(self) -> None:
        """Initialize action analyzer."""
        self.loop_threshold = 3  # Min repetitions to detect loop
        self.similar_action_time_threshold = 2.0  # seconds
        self.wait_time_threshold = 1.0  # seconds to consider as wait

    def analyze(self, actions: List[RecordedAction]) -> Dict[str, Any]:
        """Analyze recorded actions.

        Args:
            actions: List of recorded actions

        Returns:
            Analysis results
        """
        results = {
            "total_actions": len(actions),
            "patterns": [],
            "loops": [],
            "conditions": [],
            "waits": [],
            "duplicates": [],
            "suggestions": [],
        }

        if not actions:
            return results

        # Detect loops
        loops = self._detect_loops(actions)
        results["loops"] = loops
        results["patterns"].extend([p for p in loops])

        # Detect implicit waits
        waits = self._detect_waits(actions)
        results["waits"] = waits

        # Detect duplicates
        duplicates = self._detect_duplicates(actions)
        results["duplicates"] = duplicates

        # Generate optimization suggestions
        suggestions = self._generate_suggestions(actions, results)
        results["suggestions"] = suggestions

        logger.info(
            f"Analysis complete: {len(loops)} loops, {len(waits)} waits, "
            f"{len(duplicates)} duplicates, {len(suggestions)} suggestions"
        )

        return results

    def _detect_loops(self, actions: List[RecordedAction]) -> List[ActionPattern]:
        """Detect loop patterns in actions.

        Args:
            actions: List of actions

        Returns:
            Detected loop patterns
        """
        loops = []

        # Look for repeating sequences
        for i in range(len(actions)):
            for seq_len in range(1, min(10, len(actions) - i)):
                # Get sequence
                sequence = actions[i : i + seq_len]

                # Count repetitions
                repetitions = 1
                j = i + seq_len

                while j + seq_len <= len(actions):
                    next_seq = actions[j : j + seq_len]

                    if self._sequences_similar(sequence, next_seq):
                        repetitions += 1
                        j += seq_len
                    else:
                        break

                # If enough repetitions, it's a loop
                if repetitions >= self.loop_threshold:
                    loop_actions = actions[i : j]

                    pattern = ActionPattern(
                        type="loop",
                        actions=loop_actions,
                        confidence=min(1.0, repetitions / 10),
                        metadata={
                            "sequence_length": seq_len,
                            "repetitions": repetitions,
                            "start_index": i,
                            "end_index": j,
                        },
                    )

                    loops.append(pattern)

                    # Skip analyzed actions
                    return loops  # Return early to avoid overlapping loops

        return loops

    def _sequences_similar(
        self, seq1: List[RecordedAction], seq2: List[RecordedAction]
    ) -> bool:
        """Check if two action sequences are similar.

        Args:
            seq1: First sequence
            seq2: Second sequence

        Returns:
            True if similar
        """
        if len(seq1) != len(seq2):
            return False

        for a1, a2 in zip(seq1, seq2):
            # Compare action types
            if a1.type != a2.type:
                return False

            # Compare selectors (if available)
            if a1.best_selector and a2.best_selector:
                # Allow different instances of same element type
                if a1.best_selector.type != a2.best_selector.type:
                    return False

        return True

    def _detect_waits(self, actions: List[RecordedAction]) -> List[Dict[str, Any]]:
        """Detect implicit waits between actions.

        Args:
            actions: List of actions

        Returns:
            Detected waits
        """
        waits = []

        for i in range(len(actions) - 1):
            current = actions[i]
            next_action = actions[i + 1]

            # Calculate time difference
            time_diff = (next_action.timestamp - current.timestamp).total_seconds()

            if time_diff > self.wait_time_threshold:
                waits.append(
                    {
                        "before_action": i + 1,
                        "wait_time": time_diff,
                        "suggestion": f"Add explicit wait of {time_diff:.1f}s before action {i + 1}",
                    }
                )

        return waits

    def _detect_duplicates(
        self, actions: List[RecordedAction]
    ) -> List[Dict[str, Any]]:
        """Detect duplicate actions.

        Args:
            actions: List of actions

        Returns:
            Detected duplicates
        """
        duplicates = []
        seen = {}

        for i, action in enumerate(actions):
            # Create action signature
            sig = self._action_signature(action)

            if sig in seen:
                # Check if close in time
                prev_idx = seen[sig]
                time_diff = (
                    action.timestamp - actions[prev_idx].timestamp
                ).total_seconds()

                if time_diff < self.similar_action_time_threshold:
                    duplicates.append(
                        {
                            "indices": [prev_idx, i],
                            "type": action.type.value,
                            "time_diff": time_diff,
                            "suggestion": f"Remove duplicate action at index {i}",
                        }
                    )

            seen[sig] = i

        return duplicates

    def _action_signature(self, action: RecordedAction) -> str:
        """Create signature for action comparison.

        Args:
            action: Recorded action

        Returns:
            Signature string
        """
        parts = [action.type.value]

        if action.best_selector:
            parts.append(action.best_selector.value)

        if action.value:
            parts.append(action.value)

        if action.url:
            parts.append(action.url)

        return "|".join(parts)

    def _generate_suggestions(
        self, actions: List[RecordedAction], analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization suggestions.

        Args:
            actions: List of actions
            analysis: Analysis results

        Returns:
            List of suggestions
        """
        suggestions = []

        # Suggest loop optimization
        for loop in analysis.get("loops", []):
            reps = loop.metadata.get("repetitions", 0)
            suggestions.append(
                f"Loop detected: {reps} repetitions. Consider using a Loop block."
            )

        # Suggest wait optimization
        wait_count = len(analysis.get("waits", []))
        if wait_count > 0:
            suggestions.append(
                f"Found {wait_count} implicit waits. Consider adding explicit wait actions."
            )

        # Suggest duplicate removal
        dup_count = len(analysis.get("duplicates", []))
        if dup_count > 0:
            suggestions.append(f"Found {dup_count} duplicate actions to remove.")

        # Suggest combining sequential input actions
        input_sequences = self._find_input_sequences(actions)
        if input_sequences:
            suggestions.append(
                f"Found {len(input_sequences)} input sequences that could be combined."
            )

        # Suggest adding comments for complex sequences
        if len(actions) > 20:
            suggestions.append("Consider adding comments to describe workflow sections.")

        return suggestions

    def _find_input_sequences(
        self, actions: List[RecordedAction]
    ) -> List[List[RecordedAction]]:
        """Find sequences of input actions to same element.

        Args:
            actions: List of actions

        Returns:
            Input sequences
        """
        sequences = []
        current_seq = []

        for action in actions:
            if action.type in [ActionType.TYPE_TEXT, ActionType.FILL]:
                if current_seq:
                    # Check if same element
                    if (
                        action.best_selector
                        and current_seq[-1].best_selector
                        and action.best_selector.value
                        == current_seq[-1].best_selector.value
                    ):
                        current_seq.append(action)
                    else:
                        if len(current_seq) > 1:
                            sequences.append(current_seq)
                        current_seq = [action]
                else:
                    current_seq = [action]
            else:
                if len(current_seq) > 1:
                    sequences.append(current_seq)
                current_seq = []

        if len(current_seq) > 1:
            sequences.append(current_seq)

        return sequences

    def optimize_actions(
        self, actions: List[RecordedAction]
    ) -> List[OptimizedAction]:
        """Optimize recorded actions.

        Args:
            actions: Recorded actions

        Returns:
            Optimized actions
        """
        optimized = []

        # Run analysis
        analysis = self.analyze(actions)

        # Handle loops
        processed_indices = set()

        for loop_pattern in analysis.get("loops", []):
            start = loop_pattern.metadata["start_index"]
            end = loop_pattern.metadata["end_index"]
            seq_len = loop_pattern.metadata["sequence_length"]
            reps = loop_pattern.metadata["repetitions"]

            # Mark as processed
            for i in range(start, end):
                processed_indices.add(i)

            # Create optimized loop action
            loop_body = actions[start : start + seq_len]

            for action in loop_body:
                if action.best_selector:
                    opt_action = OptimizedAction(
                        original_actions=loop_pattern.actions,
                        type=ActionType.CUSTOM,
                        selector=action.best_selector,
                        is_loop=True,
                        loop_count=reps,
                        description=f"Loop: {reps} repetitions",
                    )
                    optimized.append(opt_action)
                    break

        # Add non-loop actions
        for i, action in enumerate(actions):
            if i not in processed_indices and action.best_selector:
                opt_action = OptimizedAction(
                    original_actions=[action],
                    type=action.type,
                    selector=action.best_selector,
                    value=action.value,
                    description=f"{action.type.value}",
                )
                optimized.append(opt_action)

        logger.info(f"Optimized {len(actions)} actions to {len(optimized)} actions")

        return optimized

    def detect_conditional_patterns(
        self, actions: List[RecordedAction]
    ) -> List[ActionPattern]:
        """Detect conditional execution patterns.

        Args:
            actions: List of actions

        Returns:
            Conditional patterns
        """
        patterns = []

        # Look for navigation-based conditions
        # (e.g., different actions based on which page loads)

        # Look for element-existence-based conditions
        # (e.g., click button A if exists, else button B)

        # This is a simplified version
        # In production, would use ML or more complex heuristics

        return patterns
