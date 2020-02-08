from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

from pathlib import Path


DEBUG_SKIP = False


class Script(FightScript):
    def can_spare(self):
        return True


    def get_choices(self):
        return [UseWeapon(Weapon('itt_tutorial_answer_correctly', 'Answer correctly')), Spare(), Spare()]


    async def run(self):
        if not DEBUG_SKIP:
            await display_text(load_text('fight/pre-lyceum/itt_test_cariel_tutorial'))
        menu = self.get_main_menu()
        choice = await menu.choose()
        await self.get_action_for_choice(choice)()
        get_event_manager().raise_event('fight_finished')


    async def on_kill(self):
        get_state()['itt_test_tutorial'] = 'dead'
        get_state()['pacifist_route_possible'] = False


    async def on_spare(self):
        get_state()['itt_test_tutorial'] = 'spared'
        get_state()['genocide_route_possible'] = False


async def run(*, enemy_battle, **kwargs):
    global fs
    fs = Script(enemy_battle)
    await fs.run()


async def draw(*, destination, **kwargs):
    global fs
    fs.draw(destination)
