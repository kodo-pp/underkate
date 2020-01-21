from underkate.global_game import get_game
from underkate.overworld.object import Object
from underkate.texture import load_texture
from underkate.vector import Vector

from pygame import Rect


async def main(*, root, script, **kwargs):
    texture = load_texture(root / 'flate' / 'overworld.png', scale=2)
    flate = Object(Vector(400, 150), texture=texture, is_passable=False, hitbox=Rect(-60, -30, 120, 70))
    get_game().overworld.room.add_object(flate)
    flate.on_interact = lambda: get_game().overworld.room.run_script('flate_interact')