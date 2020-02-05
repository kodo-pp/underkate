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


DEBUG_SKIP = True


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
        cariel_shouting = load_texture(self.battle.root / 'cariel' / 'face_shouting.png', scale=2)
        cariel_begging  = load_texture(self.battle.root / 'cariel' / 'face_begging.png', scale=2)
        font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        txt = DisplayedText([
            TextPage("IT Theory test attacks you", font),
            TextPage("... for example, right now", font, picture=cariel_neutral),
            TextPage("But don't be afraid! Many of the tasks\nare simple, and...", font, picture=cariel_smiling),
            TextPage("it might be not too difficult... to solve...", font, picture=cariel_neutral),
            TextPage("...", font, picture=cariel_thinking),
            TextPage("Forgive me, please. I'm a bit worried\nabout that", font, picture=cariel_neutral),
            TextPage("Teachers commit themselves into designing\nthese problems and tasks", font, picture=cariel_neutral),
            TextPage("They try very hard to put the deadlines\ninto your schedule", font, picture=cariel_neutral),
            TextPage("And what is most important is that...\n", font, picture=cariel_neutral),
            TextPage("THE POWER OF THEIR SOULS LIES IN THESE\nPROBLEMS", font, picture=cariel_shouting),
            TextPage("...", font, picture=cariel_thinking),
            TextPage("So please...", font, picture=cariel_begging),
            TextPage("Don't solve them that easily", font, picture=cariel_begging),
            TextPage("I just don't want you to hurt anyone", font, picture=cariel_smiling),
            TextPage("Alright?", font, picture=cariel_begging),
        ])
        if not DEBUG_SKIP:
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
