from underkate.global_game import get_game
from underkate.scriptlib.common import make_callback, wait_for_event


async def play_animation(animated_sprite, where=None):
    if where is None:
        where = get_game().current_game_mode
    where.spawn(animated_sprite)
    event_id, callback = make_callback()
    animated_sprite.on_stop = callback
    animated_sprite.start_animation()
    await wait_for_event(event_id)
