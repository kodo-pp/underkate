from underkate.global_game import get_game
from underkate.scriptlib.common import make_callback, wait_for_event


async def play_animation(animated_sprite):
    get_game().current_game_mode.spawn(animated_sprite)
    animated_sprite.start_animation()
    event_id, callback = make_callback()
    animated_sprite.on_stop = callback
    await wait_for_event(event_id)
