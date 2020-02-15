from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, next_frame
from underkate.scriptlib.ui import OverworldMenu
from underkate.sprite import BaseSprite


class ShopMenu(OverworldMenu):
    def get_choices(self):
        return ['Yes', 'No']


    def get_title(self):
        return ['Buy a candy for 3 coins?']


async def main(*args, **kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_1_canteen/vendors/1'))
    menu = ShopMenu()
    choice = await menu.choose()
    # TODO: actually buy the item
    get_game().overworld.unfreeze()
