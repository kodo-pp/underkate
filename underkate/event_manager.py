from collections import namedtuple
from typing import Any, Callable, Dict, Hashable, List


EventId = Hashable

EventHandler = Callable[[EventId, Any], None]

class Subscriber:
    def __init__(self, handler: EventHandler, is_persistent: bool = False):
        self.handler = handler
        self.is_persistent = is_persistent


class EventManager:
    def __init__(self):
        self.subscribers: Dict[EventId, List[Subscriber]] = {}

    def subscribe(self, event_id: EventId, subscriber: Subscriber):
        self.subscribers.setdefault(event_id, []).append(subscriber)

    def raise_event(self, event_id: EventId, argument: Any):
        subscribers = self.subscribers.get(event_id, [])
        for sub in subscribers:
            sub.handler(event_id, argument)
        
        remaining_subscribers = [sub for sub in subscribers if sub.is_persistent]
        if remaining_subscribers:
            self.subscribers[event_id] = remaining_subscribers
        else:
            self.subscribers.pop(event_id, None)


_event_manager = EventManager()

def get_event_manager():
    global _event_manager
    return _event_manager
