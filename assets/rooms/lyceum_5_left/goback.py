from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text


async def main(root, **kwargs):
    overworld = get_game().overworld
    overworld.freeze()
    await display_text(load_text('overworld/lyceum_5_left/wait'))
    await overworld.room.player.walk_x(-100)
    overworld.unfreeze()
