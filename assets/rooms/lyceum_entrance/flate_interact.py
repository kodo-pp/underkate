from underkate.animated_once_texture import load_animated_once_texture
from underkate.animated_texture import load_animated_texture
from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import display_text, sleep, make_callback, wait_for_event
from underkate.scriptlib.fight import fight
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.vector import Vector
from underkate.walking_npc import WalkingNpc

from pathlib import Path
from pygame import Rect


async def main(*, root, script, **kwargs):
    get_game().overworld.freeze()

    flate_crying    = load_texture(root / 'flate' / 'face_crying.png', scale=2)
    flate_no_face   = load_texture(root / 'flate' / 'no_face.png', scale=2)
    flate_smiling   = load_texture(root / 'flate' / 'face_smiling.png', scale=2)
    flate_thinking  = load_texture(root / 'flate' / 'face_thinking.png', scale=2)
    flate_evil      = load_texture(root / 'flate' / 'face_evil.png', scale=2)

    cariel_dissat   = load_texture(root / 'cariel' / 'face_dissatisfied.png', scale=2)
    cariel_neutral  = load_texture(root / 'cariel' / 'face_neutral.png', scale=2)
    cariel_smiling  = load_texture(root / 'cariel' / 'face_smiling.png', scale=2)
    cariel_thinking = load_texture(root / 'cariel' / 'face_thinking.png', scale=2)

    font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
    txt = DisplayedText([
        TextPage("You say hello to Flate", font),
        TextPage("...", font, picture=flate_crying),
        TextPage("It ignores you but starts to cry harder", font),
    ])

    await display_text(txt)
    await sleep(2)
    txt = DisplayedText([
        TextPage("...", font, picture=flate_no_face),
        TextPage("Hey! It looks like you're new to\nthis place, aren't you?", font, picture=flate_smiling),
        TextPage("Well, then...", font, picture=flate_thinking),
        TextPage("THAT'S YOUR PROBLEM!", font, delay=0.15, skippable=False, picture=flate_evil),
        TextPage("WHAT A PITY NOBODY GONNA\nHELP YOU!", font, delay=0.15, skippable=False, picture=flate_evil),
        TextPage("...", font, picture=flate_thinking),
        TextPage("Ah, just kidding", font, picture=flate_smiling),
        TextPage(
            "I'm Flate and I really LOVE\nscaring strangers! That's\nmy absolutely beloved hobby))",
            font,
            picture = flate_smiling,
        ),
        TextPage(
            "Anyway, you are admitted here,\nto The Lyceum, right?",
            font,
            picture = flate_smiling,
        ),
        TextPage(
            "Wow, that's wonderful!",
            font,
            picture = flate_smiling,
        ),
        TextPage(
            "You know what to do, right?\nYou will be confronted by various\nproblems, tasks and deadlines",
            font,
            picture = flate_smiling,
        ),
        TextPage(
            "Just solve 'em all, and everything's\ngonna be alright!",
            font,
            picture = flate_smiling,
        ),
        TextPage("Mwu-ha~", font, picture=flate_evil),
        TextPage("...", font, picture=flate_thinking),
        TextPage("Oh, sorry, force of habit.\nForget it!", font, picture=flate_smiling),
        TextPage("Flate! You again?", font, picture=cariel_dissat),
        TextPage("Oh no, I have to go...", font, picture=flate_thinking),
    ])
    await display_text(txt)

    animation = load_animated_once_texture(root / 'flate' / 'disappear', scale=2)
    get_game().overworld.room.state['flate_object'].texture = animation
    event_id, callback = make_callback()
    animation.on_finish = callback
    await wait_for_event(event_id)
    get_game().overworld.room.state['flate_object'].kill()

    cariel_overworld = WalkingNpc(
        pos = Vector(400, -170),
        left = load_animated_texture(root / 'cariel' / 'left', scale=2),
        right = load_animated_texture(root / 'cariel' / 'right', scale=2),
        front = load_animated_texture(root / 'cariel' / 'front', scale=2),
        back = load_animated_texture(root / 'cariel' / 'back', scale=2),
        speed = 120.0,
    )
    get_game().overworld.room.spawn(cariel_overworld)
    await cariel_overworld.walk_y(260)

    txt = DisplayedText([
        TextPage("Well... they're gone", font, picture=cariel_neutral),
        TextPage("Excuse them, please, they are a\nbit strange, you see...", font, picture=cariel_neutral),
        TextPage("...", font, picture=cariel_thinking),
        TextPage(
            """I'm Cariel, the one who helps
newcomers to achieve their goals here
and protects them through their way
in The Lyceum""",
            font,
            picture = cariel_smiling,
        ),
        TextPage("Don't be afraid, I will\ntake good care of you", font, picture=cariel_smiling),
        TextPage("...", font, picture=cariel_thinking),
        TextPage("Before we begin, you have to\nlearn some basic things", font, picture=cariel_neutral),
        TextPage(
            "First of all, while you are here,\ndeadlines and tasks may confront you",
            font,
            picture = cariel_neutral,
        ),
        TextPage(
            "For example...",
            font,
            picture = cariel_neutral,
        ),
    ])
    await display_text(txt)
    await fight(load_enemy_battle_by_name('itt_test_cariel_tutorial'))

    cariel_overworld.kill()

    get_game().overworld.unfreeze()
