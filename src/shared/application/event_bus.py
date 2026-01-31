from collections.abc import Callable
from typing import Any

from shared.domain.event import Event


class EventBus:
    """In-memory event bus for publishing domain events to subscribers."""

    def __init__(self):
        # Event -> List of Handlers
        self._subscribers: dict[type[Event], list[Callable[[Event], Any]]] = {}

    def subscribe(self, event_type: type[Event], handler: Callable[[Any], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, events: list[Event]):
        for event in events:
            handlers = self._subscribers.get(type(event), [])
            for handler in handlers:
                handler(event)
