from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, next_frame
from underkate.scriptlib.inventory import buy_item
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
    if choice == 'Yes':
        await buy_item(
            {
                'type': 'food',
                'restores': 11,
                'name': 'candy',
                'pretty_name': 'Colorful candy',
                'pretty_name2': 'a colorful candy',
            },
            price = 3,
        )
    get_game().overworld.unfreeze()
