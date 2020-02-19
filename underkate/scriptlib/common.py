from underkate.event_manager import Subscriber, get_event_manager, EventId
from underkate.global_game import get_game
from underkate.pending_callback_queue import get_pending_callback_queue

from types import coroutine
from typing import Callable, Any


@coroutine
def sleep(delay):
    script = get_game().current_script
    get_pending_callback_queue().fire_after(delay, script)
    yield


def notify_after(delay: float, event_id: EventId, argument: Any = None):
    script = get_game().current_script
    get_pending_callback_queue().fire_after(
        delay,
        lambda *args: get_event_manager().raise_event(event_id, argument),
    )


@coroutine
def wait_for_event(event_id):
    script = get_game().current_script
    get_event_manager().subscribe(event_id, Subscriber(lambda event, arg: script((event, arg))))
    return (yield)


@coroutine
def wait_for_any_event():
    script = get_game().current_script
    get_event_manager().subscribe_to_any_event(Subscriber(lambda event, arg: script((event, arg))))
    return (yield)


async def wait_for_event_by_filter(event_filter: Callable[[EventId, Any], bool]):
    while True:
        event_id, argument = await wait_for_any_event()
        if event_filter(event_id, argument):
            return event_id, argument


async def next_frame():
    await wait_for_event('end_of_cycle')


async def display_text(text):
    get_game().current_game_mode.spawn(text)
    event_id = get_event_manager().unique_id()
    text.on_finish_callback = lambda: get_event_manager().raise_event(event_id, None)
    text.initialize()
    await wait_for_event(event_id)


def make_callback():
    event_id = get_event_manager().unique_id()
    callback = lambda *args, **kwargs: get_event_manager().raise_event(event_id, None)
    return event_id, callback
