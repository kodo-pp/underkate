from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text


async def main(**kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_hall/emblem'))
    get_game().overworld.unfreeze()
