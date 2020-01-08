import time
from typing import NewType, Callable

from sortedcontainers import SortedList  # type: ignore


TimePoint = NewType('TimePoint', float)


def get_current_time() -> TimePoint:
    return TimePoint(time.monotonic())


def add_time_delta(point: TimePoint, delta: float) -> TimePoint:
    return TimePoint(point + delta)


class PendingCallback:
    def __init__(self, fire_timestamp: TimePoint, handler: Callable[[], None]):
        self.fire_timestamp = fire_timestamp
        self.handler = handler

    def handle(self):
        self.handler()

    def has_fired(self, current_timestamp: TimePoint) -> bool:
        return current_timestamp >= self.fire_timestamp

    def key(self):
        return self.fire_timestamp


class PendingCallbackQueue:
    def __init__(self):
        self.queue = SortedList(key=PendingCallback.key)
    
    def fire_after(self, delay: float, handler: Callable):
        fire_timestamp = add_time_delta(get_current_time(), delay)
        pending_callback = PendingCallback(fire_timestamp, handler)
        self.queue.add(pending_callback)

    def update(self):
        current_timestamp = get_current_time()
        num_fired_callbacks = self.queue.bisect_key_right(current_timestamp)
        fired_callbacks = self.queue[:num_fired_callbacks]
        del self.queue[:num_fired_callbacks]
        for callback in fired_callbacks:
            callback.handle()


_pending_callback_queue = PendingCallbackQueue()

def get_pending_callback_queue() -> PendingCallbackQueue:
    global _pending_callback_queue
    return _pending_callback_queue
