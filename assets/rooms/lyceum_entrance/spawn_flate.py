from underkate.texture import load_texture
from underkate.global_game import get_game
from underkate.object import Object
from underkate.vector import Vector

from pygame import Rect


async def main(*, root, script, **kwargs):
    texture = load_texture(root / 'flate' / 'overworld.png', scale=2)
    flate = Object(Vector(400, 150), texture=texture, is_passable=False, hitbox=Rect(-60, -20, 120, 40))
    get_game().overworld.room.add_object(flate)
