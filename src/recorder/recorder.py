"""
Main recorder class for recording browser actions.

Coordinates event listening, action recording, and script generation.
"""

from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import uuid
from loguru import logger

from src.recorder.types import (
    RecordedAction,
    RecordingSession,
    EventType,
    ActionType,
    ElementInfo,
)
from src.recorder.event_listener import EventListener
from src.recorder.selector_generator import SelectorGenerator
from src.recorder.action_analyzer import ActionAnalyzer
from src.recorder.script_generator import ScriptGenerator
from src.recorder.optimizer import ActionOptimizer


class Recorder:
    """Main recorder for capturing browser interactions."""

    def __init__(self, browser_controller: Any) -> None:
        """Initialize recorder.

        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        self.page = browser_controller.current_page if browser_controller else None

        # Components
        self.event_listener: Optional[EventListener] = None
        self.selector_generator = SelectorGenerator()
        self.analyzer = ActionAnalyzer()
        self.script_generator = ScriptGenerator()
        self.optimizer = ActionOptimizer()

        # Recording state
        self.is_recording = False
        self.current_session: Optional[RecordingSession] = None
        self.last_url: Optional[str] = None

        # Callbacks
        self.on_action_recorded: Optional[Callable[[RecordedAction], None]] = None

        logger.info("Recorder initialized")

    async def start_recording(self, session_name: Optional[str] = None) -> str:
        """Start recording user actions.

        Args:
            session_name: Optional session name

        Returns:
            Session ID
        """
        if self.is_recording:
            logger.warning("Already recording")
            return self.current_session.id if self.current_session else ""

        # Create new session
        session_id = str(uuid.uuid4())
        self.current_session = RecordingSession(
            id=session_id,
            start_time=datetime.now(),
            metadata={"name": session_name or "Untitled Recording"},
        )

        # Get current page
        if not self.page:
            self.page = self.browser.current_page if self.browser else None

        if not self.page:
            raise Exception("No active page to record")

        # Get start URL
        try:
            self.current_session.start_url = self.page.url
            self.last_url = self.page.url
        except Exception:
            pass

        # Create event listener
        self.event_listener = EventListener(self.page)

        # Register event handlers
        self._register_event_handlers()

        # Start listening
        await self.event_listener.start()

        self.is_recording = True

        logger.info(f"Recording started: {session_id}")

        return session_id

    async def stop_recording(self) -> RecordingSession:
        """Stop recording and finalize session.

        Returns:
            Completed recording session
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return self.current_session or RecordingSession(
                id="", start_time=datetime.now()
            )

        # Stop event listener
        if self.event_listener:
            await self.event_listener.stop()

        # Finalize session
        if self.current_session:
            self.current_session.end_time = datetime.now()

            # Get end URL
            try:
                if self.page:
                    self.current_session.end_url = self.page.url
            except Exception:
                pass

        self.is_recording = False

        logger.info(
            f"Recording stopped: {len(self.current_session.actions) if self.current_session else 0} actions"
        )

        return self.current_session

    def _register_event_handlers(self) -> None:
        """Register handlers for browser events."""
        if not self.event_listener:
            return

        # Click events
        self.event_listener.on(EventType.CLICK, self._on_click)
        self.event_listener.on(EventType.DOUBLE_CLICK, self._on_double_click)
        self.event_listener.on(EventType.RIGHT_CLICK, self._on_right_click)

        # Input events
        self.event_listener.on(EventType.INPUT, self._on_input)
        self.event_listener.on(EventType.CHANGE, self._on_change)

        # Form events
        self.event_listener.on(EventType.SUBMIT, self._on_submit)

        # Keyboard events
        self.event_listener.on(EventType.KEYDOWN, self._on_keydown)

        # Navigation events
        self.event_listener.on(EventType.NAVIGATION, self._on_navigation)

        # Scroll events
        self.event_listener.on(EventType.SCROLL, self._on_scroll)

        logger.debug("Event handlers registered")

    async def _on_click(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle click event.

        Args:
            element_info: Element information
            data: Event data
        """
        if not element_info:
            return

        # Generate selectors
        selectors = await self.selector_generator.generate_selectors(
            element_info, self.page
        )
        best_selector = self.selector_generator.get_best_selector(selectors)

        # Create action
        action = RecordedAction(
            type=ActionType.CLICK,
            timestamp=datetime.now(),
            element=element_info,
            selectors=selectors,
            best_selector=best_selector,
            modifiers=self._extract_modifiers(data),
        )

        await self._record_action(action)

    async def _on_double_click(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle double click event.

        Args:
            element_info: Element information
            data: Event data
        """
        if not element_info:
            return

        selectors = await self.selector_generator.generate_selectors(
            element_info, self.page
        )
        best_selector = self.selector_generator.get_best_selector(selectors)

        action = RecordedAction(
            type=ActionType.DOUBLE_CLICK,
            timestamp=datetime.now(),
            element=element_info,
            selectors=selectors,
            best_selector=best_selector,
        )

        await self._record_action(action)

    async def _on_right_click(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle right click event.

        Args:
            element_info: Element information
            data: Event data
        """
        if not element_info:
            return

        selectors = await self.selector_generator.generate_selectors(
            element_info, self.page
        )
        best_selector = self.selector_generator.get_best_selector(selectors)

        action = RecordedAction(
            type=ActionType.RIGHT_CLICK,
            timestamp=datetime.now(),
            element=element_info,
            selectors=selectors,
            best_selector=best_selector,
        )

        await self._record_action(action)

    async def _on_input(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle input event.

        Args:
            element_info: Element information
            data: Event data
        """
        if not element_info:
            return

        selectors = await self.selector_generator.generate_selectors(
            element_info, self.page
        )
        best_selector = self.selector_generator.get_best_selector(selectors)

        action = RecordedAction(
            type=ActionType.TYPE_TEXT,
            timestamp=datetime.now(),
            element=element_info,
            selectors=selectors,
            best_selector=best_selector,
            value=data.get("value", ""),
        )

        await self._record_action(action)

    async def _on_change(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle change event (select, checkbox, radio).

        Args:
            element_info: Element information
            data: Event data
        """
        if not element_info:
            return

        selectors = await self.selector_generator.generate_selectors(
            element_info, self.page
        )
        best_selector = self.selector_generator.get_best_selector(selectors)

        # Determine action type based on element
        action_type = ActionType.FILL

        if element_info.tag_name == "select":
            action_type = ActionType.SELECT
        elif element_info.type in ["checkbox", "radio"]:
            action_type = ActionType.CHECK if data.get("checked") else ActionType.UNCHECK

        action = RecordedAction(
            type=action_type,
            timestamp=datetime.now(),
            element=element_info,
            selectors=selectors,
            best_selector=best_selector,
            value=data.get("value", ""),
        )

        await self._record_action(action)

    async def _on_submit(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle form submit event.

        Args:
            element_info: Element information
            data: Event data
        """
        # Usually we don't need separate submit action
        # as it's handled by click on submit button
        logger.debug("Form submit event")

    async def _on_keydown(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle keydown event.

        Args:
            element_info: Element information
            data: Event data
        """
        key = data.get("key", "")

        # Only record special keys
        if key in ["Enter", "Tab", "Escape"]:
            logger.debug(f"Key pressed: {key}")

    async def _on_navigation(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle navigation event.

        Args:
            element_info: Element information
            data: Event data
        """
        url = data.get("url", "")

        if url and url != self.last_url:
            action = RecordedAction(
                type=ActionType.NAVIGATE,
                timestamp=datetime.now(),
                url=url,
            )

            await self._record_action(action)
            self.last_url = url

    async def _on_scroll(
        self, element_info: Optional[ElementInfo], data: Dict[str, Any]
    ) -> None:
        """Handle scroll event.

        Args:
            element_info: Element information
            data: Event data
        """
        action = RecordedAction(
            type=ActionType.SCROLL,
            timestamp=datetime.now(),
            position={
                "x": data.get("scrollX", 0),
                "y": data.get("scrollY", 0),
            },
        )

        await self._record_action(action)

    async def _record_action(self, action: RecordedAction) -> None:
        """Record action to current session.

        Args:
            action: Action to record
        """
        if not self.current_session:
            return

        self.current_session.add_action(action)

        logger.debug(
            f"Recorded: {action.type.value} "
            f"({len(self.current_session.actions)} total)"
        )

        # Call callback if set
        if self.on_action_recorded:
            self.on_action_recorded(action)

    def _extract_modifiers(self, data: Dict[str, Any]) -> List[str]:
        """Extract keyboard modifiers from event data.

        Args:
            data: Event data

        Returns:
            List of modifier keys
        """
        modifiers = []

        if data.get("ctrlKey"):
            modifiers.append("Control")
        if data.get("shiftKey"):
            modifiers.append("Shift")
        if data.get("altKey"):
            modifiers.append("Alt")
        if data.get("metaKey"):
            modifiers.append("Meta")

        return modifiers

    def get_recorded_actions(self) -> List[RecordedAction]:
        """Get all recorded actions.

        Returns:
            List of recorded actions
        """
        if not self.current_session:
            return []

        return self.current_session.actions

    def optimize_recording(self) -> List[RecordedAction]:
        """Optimize recorded actions.

        Returns:
            Optimized actions
        """
        if not self.current_session:
            return []

        return self.optimizer.optimize(self.current_session.actions)

    def analyze_recording(self) -> Dict[str, Any]:
        """Analyze recorded actions.

        Returns:
            Analysis results
        """
        if not self.current_session:
            return {}

        return self.analyzer.analyze(self.current_session.actions)

    def generate_workflow_blocks(self) -> List[Dict[str, Any]]:
        """Generate workflow blocks from recording.

        Returns:
            Workflow blocks
        """
        if not self.current_session:
            return []

        # Optimize first
        optimized = self.optimize_recording()

        # Generate blocks
        return self.script_generator.generate_workflow_blocks(optimized)

    def generate_python_script(
        self, framework: str = "playwright"
    ) -> str:
        """Generate Python script from recording.

        Args:
            framework: Framework to use (playwright, selenium)

        Returns:
            Python code
        """
        if not self.current_session:
            return ""

        # Optimize first
        optimized = self.optimize_recording()

        # Generate script
        if framework == "playwright":
            return self.script_generator.generate_python_playwright(optimized)
        elif framework == "selenium":
            return self.script_generator.generate_python_selenium(optimized)
        else:
            raise ValueError(f"Unknown framework: {framework}")

    def save_session(self, file_path: Path) -> bool:
        """Save recording session to file.

        Args:
            file_path: Path to save session

        Returns:
            True if successful
        """
        if not self.current_session:
            logger.error("No session to save")
            return False

        try:
            import json

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.current_session.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Session saved to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def load_session(self, file_path: Path) -> bool:
        """Load recording session from file.

        Args:
            file_path: Path to load session from

        Returns:
            True if successful
        """
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Reconstruct session
            # This is simplified - would need full deserialization
            session_id = data.get("id", str(uuid.uuid4()))
            start_time = datetime.fromisoformat(data.get("start_time"))

            self.current_session = RecordingSession(
                id=session_id,
                start_time=start_time,
                metadata=data.get("metadata", {}),
            )

            if data.get("end_time"):
                self.current_session.end_time = datetime.fromisoformat(
                    data["end_time"]
                )

            logger.info(f"Session loaded from: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
