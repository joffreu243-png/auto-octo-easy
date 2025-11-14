"""
Browser event listener for recording user actions.

Injects JavaScript into pages to capture user events and sends them to Python.
"""

from typing import Callable, Dict, Any, Optional, List
from loguru import logger
import json
import asyncio

from src.recorder.types import EventType, ElementInfo


class EventListener:
    """Listens to browser events and forwards them to recorder."""

    def __init__(self, page: Any) -> None:
        """Initialize event listener.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.is_listening = False
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self._debounce_timers: Dict[str, asyncio.Task] = {}
        self._last_event_time: Dict[EventType, float] = {}

    async def start(self) -> None:
        """Start listening to events."""
        if self.is_listening:
            logger.warning("Already listening to events")
            return

        # Inject event capture script
        await self._inject_capture_script()

        # Setup CDP listener for custom events
        await self._setup_cdp_listener()

        self.is_listening = True
        logger.info("Event listener started")

    async def stop(self) -> None:
        """Stop listening to events."""
        if not self.is_listening:
            return

        # Remove injected scripts
        await self._remove_capture_script()

        self.is_listening = False
        logger.info("Event listener stopped")

    def on(self, event_type: EventType, handler: Callable) -> None:
        """Register event handler.

        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type.value}")

    def off(self, event_type: EventType, handler: Callable) -> None:
        """Unregister event handler.

        Args:
            event_type: Type of event
            handler: Handler function
        """
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for {event_type.value}")
            except ValueError:
                pass

    async def _inject_capture_script(self) -> None:
        """Inject JavaScript to capture events."""
        script = """
        (function() {
            // Prevent multiple injections
            if (window.__octoRecorderInjected) return;
            window.__octoRecorderInjected = true;

            // Helper to get element info
            function getElementInfo(element) {
                const rect = element.getBoundingClientRect();
                const computedStyle = window.getComputedStyle(element);

                // Get XPath
                function getXPath(el) {
                    if (el.id) return `//*[@id="${el.id}"]`;
                    if (el === document.body) return '/html/body';

                    let position = 0;
                    let siblings = el.parentNode.childNodes;
                    for (let i = 0; i < siblings.length; i++) {
                        let sibling = siblings[i];
                        if (sibling === el) {
                            return getXPath(el.parentNode) + '/' + el.tagName.toLowerCase() +
                                   '[' + (position + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === el.tagName) {
                            position++;
                        }
                    }
                }

                // Get CSS path
                function getCSSPath(el) {
                    if (el.id) return '#' + el.id;
                    if (el === document.body) return 'body';

                    let path = [];
                    while (el.parentElement) {
                        let selector = el.tagName.toLowerCase();
                        if (el.id) {
                            selector = '#' + el.id;
                            path.unshift(selector);
                            break;
                        } else {
                            let sibling = el;
                            let nth = 1;
                            while (sibling.previousElementSibling) {
                                sibling = sibling.previousElementSibling;
                                if (sibling.tagName === el.tagName) nth++;
                            }
                            if (nth > 1) selector += ':nth-of-type(' + nth + ')';
                        }
                        path.unshift(selector);
                        el = el.parentElement;
                    }
                    return path.join(' > ');
                }

                return {
                    tag_name: element.tagName.toLowerCase(),
                    id: element.id || null,
                    classes: Array.from(element.classList),
                    name: element.name || null,
                    placeholder: element.placeholder || null,
                    aria_label: element.getAttribute('aria-label') || null,
                    data_testid: element.getAttribute('data-testid') || null,
                    data_qa: element.getAttribute('data-qa') || null,
                    role: element.getAttribute('role') || null,
                    text: element.textContent ? element.textContent.trim().substring(0, 100) : null,
                    value: element.value || null,
                    type: element.type || null,
                    href: element.href || null,
                    src: element.src || null,
                    xpath: getXPath(element),
                    css_path: getCSSPath(element),
                    position: {
                        x: rect.left + window.scrollX,
                        y: rect.top + window.scrollY,
                        width: rect.width,
                        height: rect.height
                    }
                };
            }

            // Send event to Python
            function sendEvent(type, data) {
                window.__octoRecorderEvents = window.__octoRecorderEvents || [];
                window.__octoRecorderEvents.push({
                    type: type,
                    timestamp: Date.now(),
                    data: data
                });

                // Trigger custom event
                window.dispatchEvent(new CustomEvent('__octo_event', {
                    detail: { type, data }
                }));
            }

            // Click events
            document.addEventListener('click', (e) => {
                sendEvent('click', {
                    element: getElementInfo(e.target),
                    button: e.button,
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey,
                    metaKey: e.metaKey
                });
            }, true);

            // Double click
            document.addEventListener('dblclick', (e) => {
                sendEvent('dblclick', {
                    element: getElementInfo(e.target)
                });
            }, true);

            // Right click
            document.addEventListener('contextmenu', (e) => {
                sendEvent('contextmenu', {
                    element: getElementInfo(e.target)
                });
            }, true);

            // Input events (debounced)
            let inputTimer;
            document.addEventListener('input', (e) => {
                clearTimeout(inputTimer);
                inputTimer = setTimeout(() => {
                    sendEvent('input', {
                        element: getElementInfo(e.target),
                        value: e.target.value
                    });
                }, 500);  // Debounce 500ms
            }, true);

            // Change events
            document.addEventListener('change', (e) => {
                sendEvent('change', {
                    element: getElementInfo(e.target),
                    value: e.target.value
                });
            }, true);

            // Form submit
            document.addEventListener('submit', (e) => {
                sendEvent('submit', {
                    element: getElementInfo(e.target)
                });
            }, true);

            // Keyboard events
            document.addEventListener('keydown', (e) => {
                // Only record special keys and combinations
                if (e.key === 'Enter' || e.key === 'Tab' || e.ctrlKey || e.metaKey) {
                    sendEvent('keydown', {
                        element: getElementInfo(e.target),
                        key: e.key,
                        code: e.code,
                        ctrlKey: e.ctrlKey,
                        shiftKey: e.shiftKey,
                        altKey: e.altKey,
                        metaKey: e.metaKey
                    });
                }
            }, true);

            // Focus events
            document.addEventListener('focus', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
                    e.target.tagName === 'SELECT') {
                    sendEvent('focus', {
                        element: getElementInfo(e.target)
                    });
                }
            }, true);

            // Scroll events (debounced)
            let scrollTimer;
            document.addEventListener('scroll', (e) => {
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(() => {
                    sendEvent('scroll', {
                        scrollX: window.scrollX,
                        scrollY: window.scrollY
                    });
                }, 1000);  // Debounce 1s
            }, true);

            console.log('[OctoRecorder] Event capture injected');
        })();
        """

        try:
            await self.page.evaluate(script)
            logger.info("Event capture script injected")
        except Exception as e:
            logger.error(f"Failed to inject capture script: {e}")
            raise

    async def _setup_cdp_listener(self) -> None:
        """Setup Chrome DevTools Protocol listener for custom events."""
        # Listen for console messages containing our events
        self.page.on("console", self._handle_console_message)

        # Poll for events periodically
        asyncio.create_task(self._poll_events())

    async def _poll_events(self) -> None:
        """Poll for captured events from injected script."""
        while self.is_listening:
            try:
                # Get events from page
                events = await self.page.evaluate("""
                    () => {
                        const events = window.__octoRecorderEvents || [];
                        window.__octoRecorderEvents = [];
                        return events;
                    }
                """)

                # Process each event
                for event_data in events:
                    await self._process_event(event_data)

                # Wait before next poll
                await asyncio.sleep(0.1)  # 100ms polling interval

            except Exception as e:
                if self.is_listening:  # Only log if we're still supposed to be listening
                    logger.error(f"Error polling events: {e}")
                await asyncio.sleep(1)

    async def _process_event(self, event_data: Dict[str, Any]) -> None:
        """Process captured event.

        Args:
            event_data: Event data from JavaScript
        """
        try:
            event_type_str = event_data.get("type")
            event_type = EventType(event_type_str)

            # Convert element data to ElementInfo
            element_data = event_data.get("data", {}).get("element")
            element_info = None

            if element_data:
                element_info = ElementInfo(
                    tag_name=element_data.get("tag_name", ""),
                    id=element_data.get("id"),
                    classes=element_data.get("classes", []),
                    name=element_data.get("name"),
                    placeholder=element_data.get("placeholder"),
                    aria_label=element_data.get("aria_label"),
                    data_testid=element_data.get("data_testid"),
                    data_qa=element_data.get("data_qa"),
                    role=element_data.get("role"),
                    text=element_data.get("text"),
                    value=event_data.get("data", {}).get("value") or element_data.get("value"),
                    type=element_data.get("type"),
                    href=element_data.get("href"),
                    src=element_data.get("src"),
                    xpath=element_data.get("xpath"),
                    css_path=element_data.get("css_path"),
                )

            # Call registered handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(element_info, event_data.get("data", {}))
                    except Exception as e:
                        logger.error(f"Handler error for {event_type.value}: {e}")

        except ValueError:
            # Unknown event type
            logger.debug(f"Unknown event type: {event_data.get('type')}")
        except Exception as e:
            logger.error(f"Error processing event: {e}")

    async def _handle_console_message(self, msg) -> None:
        """Handle console messages.

        Args:
            msg: Console message
        """
        # Just for debugging
        if "__octo" in msg.text.lower():
            logger.debug(f"Console: {msg.text}")

    async def _remove_capture_script(self) -> None:
        """Remove injected capture script."""
        try:
            await self.page.evaluate("""
                () => {
                    window.__octoRecorderInjected = false;
                    window.__octoRecorderEvents = [];
                }
            """)
            logger.info("Event capture script removed")
        except Exception as e:
            logger.error(f"Failed to remove capture script: {e}")

    async def capture_navigation(self, url: str) -> None:
        """Manually capture navigation event.

        Args:
            url: Navigated URL
        """
        event_type = EventType.NAVIGATION

        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(None, {"url": url})
                except Exception as e:
                    logger.error(f"Handler error for navigation: {e}")
