from underkate.global_game import get_game
from underkate.text import DisplayedText, TextPage
from underkate.font import load_font

from pathlib import Path
from pygame import Rect


async def main(*, root, script, **kwargs):
    font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
    txt = DisplayedText([
        TextPage('You say hello to Flate', font),
        TextPage('It ignores you but starts to cry harder', font),
    ])
    get_game().overworld.spawn(txt)
    txt.initialize()
