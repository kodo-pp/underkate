from underkate.animated_texture import AnimatedTexture
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_walking_sprite import TexturedWalkingSprite


async def main(root, **kwargs):
    overworld = get_game().overworld
    overworld.freeze()

    await display_text(load_text('overworld/lyceum_5_left/grumpylook'))

    room = overworld.room

    grumpylook_object = room.named_objects['grumpylook']
    pos = grumpylook_object.pos
    grumpylook_object.kill()
    del grumpylook_object

    texture = AnimatedTexture([load_texture(root / 'grumpylook' / 'overworld.png')], fps=1)
    grumpylook = TexturedWalkingSprite(
        pos = pos,
        left = texture,
        right = texture,
        front = texture,
        back = texture,
        speed = 280,
    )
    room.spawn(grumpylook)

    await grumpylook.walk_x(700)
    grumpylook.kill()
    get_state()['grumpylook_gone'] = True
    overworld.unfreeze()
