from __future__ import annotations

from collections import defaultdict
from typing import Callable


EventHandler = Callable[[str, dict], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict) -> None:
        for handler in self._subscribers[event_name]:
            handler(event_name, payload)
