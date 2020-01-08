from collections import namedtuple
from typing import Any, Callable, Dict, Hashable, List

from loguru import logger


EventId = Hashable

EventHandler = Callable[[EventId, Any], None]

class Subscriber:
    def __init__(self, handler: EventHandler, is_persistent: bool = False):
        self.handler = handler
        self.is_persistent = is_persistent


class EventManager:
    def __init__(self):
        self.subscribers: Dict[EventId, List[Subscriber]] = {}
        self._counter = 0

    def unique_id(self) -> EventId:
        event_id = self._counter
        self._counter += 1
        logger.debug('EventManager: unique_id: {}', event_id)
        return event_id

    def subscribe(self, event_id: EventId, subscriber: Subscriber):
        logger.debug('EventManager: subscribe: `{}`', event_id)
        self.subscribers.setdefault(event_id, []).append(subscriber)

    def raise_event(self, event_id: EventId, argument: Any):
        logger.debug('EventManager: raise_event: `{}` with argument `{}`', event_id, argument)
        subscribers = self.subscribers.get(event_id, [])
        for sub in subscribers:
            sub.handler(event_id, argument)
        
        remaining_subscribers = [sub for sub in subscribers if sub.is_persistent]
        if remaining_subscribers:
            self.subscribers[event_id] = remaining_subscribers
        else:
            self.subscribers.pop(event_id, None)


_event_manager = EventManager()

def get_event_manager() -> EventManager:
    global _event_manager
    return _event_manager
