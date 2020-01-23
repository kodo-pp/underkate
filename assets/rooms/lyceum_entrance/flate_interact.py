from underkate.font import load_font
from underkate.global_game import get_game
from underkate.python_functions import display_text, sleep, make_callback, wait_for_event
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture

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

    font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
    txt = DisplayedText([
        TextPage("You say hello to Flate", font),
        TextPage("...", font, picture=flate_crying),
        TextPage("It ignores you but starts to cry harder", font),
    ])
    await display_text(script, txt)
    await sleep(script, 2)
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
            "Anyway, you are admitted here,\nto The Lyceum, right?\nWow, that's wonderful!",
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
    await display_text(script, txt)

    animation = load_animated_once_texture(root / 'flate' / 'disappear')
    get_game().overworld.room.state['flate_object'].texture = animation
    event_id, callback = make_callback()
    animation.on_finish = callback
    await wait_for_event(script, event_id)
    get_game().overworld.room.state['flate_object'].kill()
    get_game().overworld.unfreeze()
