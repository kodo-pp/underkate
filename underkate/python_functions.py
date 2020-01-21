from underkate.pending_callback_queue import get_pending_callback_queue
from underkate.event_manager import Subscriber, get_event_manager

from types import coroutine


@coroutine
def sleep(script, delay):
    get_pending_callback_queue().fire_after(delay, script)
    yield


@coroutine
def wait_for_event(script, event_id):
    get_event_manager().subscribe(event_id, Subscriber(script))
    yield
