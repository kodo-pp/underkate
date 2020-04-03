from underkate.event_manager import Subscriber, get_event_manager
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
        del event, arg
        nonlocal counter
        counter += 1
        if counter == num_awaitables:
            get_event_manager().raise_event(all_finished_event)
        else:
            get_event_manager().subscribe(one_finished_event, Subscriber(handler))

    get_event_manager().subscribe(one_finished_event, Subscriber(handler))

    for aw in awaitables:
        # WARNING: this code is potentially dangerous, since `aw`, which is changed
        # by the outer loop, is captured by the inner function. In this very case,
        # however, everything is fine, because that function is called immediately
        # and is then discarded.
        #
        # TODO: refactor this code to make it more robust and to silence Pylint's
        # cell-var-from-import warning
        async def await_and_notify(*args, **kwargs):
            del args, kwargs
            await aw
            get_event_manager().raise_event(one_finished_event)

        SimpleScript(await_and_notify)()

    await wait_for_event(all_finished_event)
