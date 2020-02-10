from underkate.global_game import get_game
from underkate.overworld.object import Object
from underkate.script import TextScript
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.vector import Vector

from pygame import Rect


async def maybe_spawn_grumpylook(root):
    texture = load_texture(root / 'grumpylook' / 'overworld.png', scale=1)
    grumpy = Object(Vector(281, 281), texture=texture, is_passable=False, hitbox=Rect(-20, -40, 40, 80))
    get_game().overworld.room.add_object(grumpy)
    grumpy.on_interact = TextScript('overworld/lyceum_1_right/grumpylook')


async def maybe_spawn_sportick(root):
    texture = load_texture(root / 'sportick' / 'overworld.png', scale=2)
    grumpy = Object(Vector(486, 293), texture=texture, is_passable=False, hitbox=Rect(-40, -90, 80, 180))
    get_game().overworld.room.add_object(grumpy)
    grumpy.on_interact = TextScript('overworld/lyceum_1_right/sportick')


async def main(*, root, **kwargs):
    await maybe_spawn_grumpylook(root)
    await maybe_spawn_sportick(root)

