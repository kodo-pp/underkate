from collections import namedtuple
from typing import Any, Callable, Dict, Hashable, List, Tuple

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
        self._lock_level = 0
        self._write_queue: List[Tuple[EventId, Subscriber]] = []


    def __enter__(self):
        self._lock_level += 1
        return self


    def __exit__(self, *args):
        self._lock_level -= 1
        if self._lock_level == 0:
            self._finalize_lock()


    def unique_id(self) -> EventId:
        event_id = self._counter
        self._counter += 1
        logger.debug('EventManager: unique_id: {}', event_id)
        return event_id


    def subscribe(self, event_id: EventId, subscriber: Subscriber):
        logger.debug('EventManager: subscribe: `{}`', event_id)
        if self._is_locked():
            self._write_queue.append((event_id, subscriber))
        else:
            with self:
                self.subscribers.setdefault(event_id, []).append(subscriber)


    def raise_event(self, event_id: EventId, argument: Any = None, silent: bool = False):
        if not silent:
            logger.debug('EventManager: raise_event: `{}` with argument `{}`', event_id, argument)
        if self._is_locked():
            # TODO: nested raise_event()
            raise NotImplementedError()
        with self:
            subscribers = self.subscribers.get(event_id, [])
            remaining_subscribers = [sub for sub in subscribers if sub.is_persistent]
            if remaining_subscribers:
                self.subscribers[event_id] = remaining_subscribers
            else:
                self.subscribers.pop(event_id, None)
        for sub in subscribers:
            sub.handler(event_id, argument)


    def _is_locked(self) -> bool:
        return self._lock_level > 0


    def _finalize_lock(self):
        assert not self._is_locked()
        for event_id, subscriber in self._write_queue:
            self.subscribers.setdefault(event_id, []).append(subscriber)
        self._write_queue = []


_event_manager = EventManager()

def get_event_manager() -> EventManager:
    global _event_manager
    return _event_manager
