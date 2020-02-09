from underkate.global_game import get_game
from underkate.overworld.object import Object
from underkate.script import TextScript
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.vector import Vector

from pygame import Rect


async def main(*, root, **kwargs):
    if get_state().get('grumpylook_lyceum_1_right_met', False):
        return

    texture = load_texture(root / 'grumpylook' / 'overworld.png', scale=1)
    grumpy = Object(Vector(382, 253), texture=texture, is_passable=False, hitbox=Rect(-20, -40, 40, 80))
    get_game().overworld.room.add_object(grumpy)
    grumpy.on_interact = TextScript('overworld/lyceum_1_right/grumpylook')
