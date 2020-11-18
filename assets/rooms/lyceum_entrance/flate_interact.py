from underkate.animated_once_texture import load_animated_once_texture
from underkate.animated_texture import load_animated_texture
from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep, make_callback, wait_for_event
from underkate.scriptlib.fight import fight
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.vector import Vector
from underkate.textured_walking_sprite import TexturedWalkingSprite

from pathlib import Path
from pygame import Rect


DEBUG_SKIP = False


async def main(*, root, script, **kwargs):
    global DEBUG_SKIP
    get_game().overworld.freeze()

    if not DEBUG_SKIP:
        await display_text(load_text('overworld/lyceum_entrance/flate-interact/1-crying'))
        await sleep(2)
    if not DEBUG_SKIP:
        await display_text(load_text('overworld/lyceum_entrance/flate-interact/2-flate-speech'))

    animation = load_animated_once_texture(root / 'flate' / 'disappear', scale=2)
    flate = get_game().overworld.room.named_objects['flate']
    flate.texture = animation
    event_id, callback = make_callback()
    animation.on_finish = callback
    await wait_for_event(event_id)
    flate.kill()

    cariel_overworld = TexturedWalkingSprite(
        pos = Vector(400, -170),
        left = load_animated_texture(root / 'cariel' / 'left', scale=2),
        right = load_animated_texture(root / 'cariel' / 'right', scale=2),
        front = load_animated_texture(root / 'cariel' / 'front', scale=2),
        back = load_animated_texture(root / 'cariel' / 'back', scale=2),
        speed = 120.0,
    )
    get_game().overworld.room.spawn(cariel_overworld)
    await cariel_overworld.walk_y(260)

    if not DEBUG_SKIP:
        await display_text(load_text('overworld/lyceum_entrance/flate-interact/3-cariel-pre-fight'))
    await fight(load_enemy_battle_by_name('itt_test_cariel_tutorial'))

    if not DEBUG_SKIP:
        if get_state()['itt_test_tutorial'] == 'dead':
            await display_text(load_text('overworld/lyceum_entrance/flate-interact/4-cariel-post-fight-kill'))
        else:
            await display_text(load_text('overworld/lyceum_entrance/flate-interact/4-cariel-post-fight-spare'))

    await cariel_overworld.walk_y(-260)
    cariel_overworld.kill()

    get_game().overworld.unfreeze()
