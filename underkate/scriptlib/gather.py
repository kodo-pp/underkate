from underkate.event_manager import Subscriber, get_event_manager, EventId
from underkate.script import SimpleScript
from underkate.scriptlib.common import wait_for_event


async def gather(*awaitables):
    # XXX: This code is fascinatingly awful, but it serves for a good purpose,
    # allowing awaiting multiple coroutines at the same time
    one_finished_event = get_event_manager().unique_id()
    all_finished_event = get_event_manager().unique_id()

    counter = 0
    num_awaitables = len(awaitables)

    def handler(event, arg):
        nonlocal counter
        counter += 1
        if counter == num_awaitables:
            get_event_manager().raise_event(all_finished_event)
        else:
            get_event_manager().subscribe(one_finished_event, Subscriber(handler))

    get_event_manager().subscribe(one_finished_event, Subscriber(handler))

    for aw in awaitables:
        async def await_and_notify(*args, **kwargs):
            await aw
            get_event_manager().raise_event(one_finished_event)

        SimpleScript(await_and_notify)()

    await wait_for_event(all_finished_event)
