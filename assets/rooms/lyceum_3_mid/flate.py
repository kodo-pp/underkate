from underkate.animated_texture import AnimatedTexture
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_walking_sprite import TexturedWalkingSprite


def determine_route():
    state = get_state()
    if state['pacifist_route_possible'] and state['genocide_route_possible']:
        return 'cheater'
    elif state['pacifist_route_possible']:
        return 'pacifist'
    elif state['genocide_route_possible']:
        return 'genocide'
    else:
        return 'neutral'


async def main(*, root, **kwargs):
    overworld = get_game().overworld
    room = overworld.room
    overworld.freeze()

    await sleep(0.8)
    old_flate = room.named_objects['flate']
    old_flate.texture = load_texture(root / 'flate' / 'overworld_neutral.png', scale=2)
    await sleep(0.8)

    route = determine_route()
    if route not in ['cheater', 'pacifist', 'neutral', 'genocide']:
        raise NotImplementedError(f'Unknown route: {repr(route)}')
    text_name = f'overworld/lyceum_3_mid/flate/{route}'
    await display_text(load_text(text_name))

    flate_texture = AnimatedTexture([old_flate.texture], fps=1)

    flate = TexturedWalkingSprite(
        pos = old_flate.pos,
        left = flate_texture,
        right = flate_texture,
        front = flate_texture,
        back = flate_texture,
        speed = 240,
    )
    room.spawn(flate)
    old_flate.kill()
    await flate.walk_x(-500)
    get_state()['lyceum_3_flate_met'] = True
    overworld.unfreeze()
