from underkate.animated_texture import AnimatedTexture
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.vector import Vector
from underkate.walking_npc import WalkingNpc


async def main(*args, root, **kwargs):
    game = get_game()
    room = game.overworld.room
    game.overworld.freeze()
    room.named_objects['grumpylook'].kill()
    texture = AnimatedTexture([load_texture(root / 'grumpylook' / 'overworld.png')], fps=1)

    grumpy = WalkingNpc(
        pos = Vector(840, 360),
        left = texture,
        right = texture,
        front = texture,
        back = texture,
        speed = 200.0,
    )
    room.spawn(grumpy)

    await display_text(load_text('overworld/lyceum_hall/grumpylook/wait/1'))
    await grumpy.walk_x(-620)
    await display_text(load_text('overworld/lyceum_hall/grumpylook/wait/2'))
    await grumpy.walk_x(-240)
    grumpy.kill()
    get_state()['grumpylook_met'] = True
    game.overworld.unfreeze()
