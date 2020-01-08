import time
from typing import NewType, Callable

from sortedcontainers import SortedList  # type: ignore


class PendingCallback:
    def __init__(self, fire_timestamp: float, handler: Callable[[], None]):
        self.fire_timestamp = fire_timestamp
        self.handler = handler

    def handle(self):
        self.handler()

    def has_fired(self, current_timestamp: float) -> bool:
        return current_timestamp >= self.fire_timestamp

    def key(self):
        return self.fire_timestamp


class PendingCallbackQueue:
    def __init__(self):
        self.queue = SortedList(key=PendingCallback.key)
    
    def fire_after(self, delay: float, handler: Callable):
        fire_timestamp = time.monotonic() + delay
        pending_callback = PendingCallback(fire_timestamp, handler)
        self.queue.add(pending_callback)

    def update(self):
        current_timestamp = time.monotonic()
        num_fired_callbacks = self.queue.bisect_key_right(current_timestamp)
        fired_callbacks = self.queue[:num_fired_callbacks]
        del self.queue[:num_fired_callbacks]
        for callback in fired_callbacks:
            callback.handle()


_pending_callback_queue = PendingCallbackQueue()

def get_pending_callback_queue() -> PendingCallbackQueue:
    global _pending_callback_queue
    return _pending_callback_queue
