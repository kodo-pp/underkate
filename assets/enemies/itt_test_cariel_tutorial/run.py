from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

from pathlib import Path


class Script(FightScript):
    def can_spare(self):
        return True


    def get_choices(self):
        return [UseWeapon(Weapon('itt_tutorial_answer_correctly', 'Answer correctly')), Spare(), Spare()]


    async def run(self):
        cariel_dissat   = load_texture(self.battle.root / 'cariel' / 'face_dissatisfied.png', scale=2)
        cariel_neutral  = load_texture(self.battle.root / 'cariel' / 'face_neutral.png', scale=2)
        cariel_smiling  = load_texture(self.battle.root / 'cariel' / 'face_smiling.png', scale=2)
        cariel_thinking = load_texture(self.battle.root / 'cariel' / 'face_thinking.png', scale=2)
        itt_test = TexturedSprite(Vector(400, 200), self.textures['itt_test'])
        get_game().current_game_mode.spawn(itt_test)
        font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        txt = DisplayedText([
            TextPage("IT Theory test attacks you", font),
            TextPage("... for example, right now", font, picture=cariel_neutral),
            TextPage("But don't be afraid! Many of the tasks\nare simple, and...", font),
            TextPage("it might be not too difficult... to solve...", font),
            TextPage("...", font),
            TextPage("Forgive me, please. I'm a bit worried\nabout that", font),
            TextPage("Teachers commit themselves into designing\nthese problems and tasks", font),
            TextPage("They try very hard to put the deadlines\ninto your schedule", font),
            TextPage("And what is most important is that...\n", font),
            TextPage("THE POWER OF THEIR SOULS LIES IN THESE\nPROBLEMS", font),
            TextPage("...", font),
            TextPage("So please...", font),
            TextPage("Don't solve them that easily", font),
            TextPage("I just don't want you to hurt anyone", font),
            TextPage("Alright?", font),
        ])
        await display_text(txt)
        menu = self.get_main_menu()
        choice = await menu.choose()
        await self.get_action_for_choice(choice)()
        get_event_manager().raise_event('fight_finished')


async def run(*, enemy_battle, **kwargs):
    global fs
    fs = Script(enemy_battle)
    await fs.run()


async def draw(*, destination, **kwargs):
    global fs
    fs.draw(destination)
