from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

from pathlib import Path


class Script(FightScript):
    def can_spare(self):
        return True


    def get_choices(self):
        return [UseWeapon(Weapon('Test weapon', 'Test weapon')), Spare()]


    async def on_kill(self):
        get_state()['pacifist_route_possible'] = False


    async def on_spare(self):
        get_state()['genocide_route_possible'] = False


async def run(*, enemy_battle, **kwargs):
    global fs
    fs = Script(enemy_battle)
    await fs.run()


async def draw(*, destination, **kwargs):
    global fs
    fs.draw(destination)


async def update(*, time_delta, **kwargs):
    global fs
    fs.update(time_delta)
