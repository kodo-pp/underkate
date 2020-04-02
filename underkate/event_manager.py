from underkate.wal_list import WalList

from typing import Any, Callable, Dict, Hashable

from loguru import logger


EventId = Hashable
EventHandler = Callable[[EventId, Any], None]


class Subscriber:
    def __init__(self, handler: EventHandler, is_persistent: bool = False):
        self.handler = handler
        self.is_persistent = is_persistent


# TODO: rewrite locking and _write_queue using WalList
class EventManager:
    def __init__(self):
        self.subscribers: Dict[EventId, WalList[Subscriber]] = {}
        self.any_subscribers: WalList[Subscriber] = WalList([])
        self._counter = 0


    def unique_id(self) -> EventId:
        event_id = self._counter
        self._counter += 1
        return event_id


    def subscribe(self, event_id: EventId, subscriber: Subscriber):
        logger.debug('EventManager: subscribe: `{}`', event_id)
        ls = self.subscribers.setdefault(event_id, WalList([]))
        with ls:
            ls.append(subscriber)


    def subscribe_to_any_event(self, subscriber: Subscriber):
        logger.debug('EventMabager: subscribe to any')
        self.any_subscribers.append(subscriber)


    def raise_event(self, event_id: EventId, argument: Any = None, silent: bool = False):
        if not silent:
            logger.debug('EventManager: raise_event: `{}` with argument `{}`', event_id, argument)

        subscribers = self.subscribers.get(event_id, WalList([]))
        with subscribers:
            for sub in subscribers:
                sub.handler(event_id, argument)
            subscribers.filter(lambda x: x.is_persistent, now=True)
        if len(subscribers) == 0:
            self.subscribers.pop(event_id, None)

        with self.any_subscribers:
            for sub in self.any_subscribers:
                sub.handler(event_id, argument)
            self.any_subscribers.filter(lambda sub: sub.is_persistent, now=True)


_event_manager = EventManager()

def get_event_manager() -> EventManager:
    global _event_manager
    return _event_manager
