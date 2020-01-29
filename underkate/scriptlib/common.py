from underkate.event_manager import Subscriber, get_event_manager
from underkate.global_game import get_game
from underkate.pending_callback_queue import get_pending_callback_queue

from types import coroutine


@coroutine
def sleep(delay):
    script = get_game().current_script
    get_pending_callback_queue().fire_after(delay, script)
    yield


@coroutine
def wait_for_event(event_id):
    script = get_game().current_script
    get_event_manager().subscribe(event_id, Subscriber(lambda event, arg: script((event, arg))))
    return (yield)


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
