from underkate.font import load_font
from underkate.global_game import get_game
from underkate.python_functions import display_text, sleep
from underkate.text import DisplayedText, TextPage

from pathlib import Path
from pygame import Rect


async def main(*, root, script, **kwargs):
    get_game().overworld.freeze()
    font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
    txt = DisplayedText([
        TextPage('You say hello to Flate', font),
        TextPage('...', font),
        TextPage('It ignores you but starts to cry harder', font),
    ])
    await display_text(script, txt)
    await sleep(script, 2)
    txt = DisplayedText([
        TextPage('...', font),
        TextPage('Oh, you are here...', font),
        TextPage('I didnt expect a company so soon', font),
    ])
    await display_text(script, txt)
    get_game().overworld.unfreeze()
