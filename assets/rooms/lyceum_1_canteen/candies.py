from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, next_frame
from underkate.scriptlib.ui import OverworldMenu
from underkate.sprite import BaseSprite


class ShopMenu(OverworldMenu):
    def __init__(self):
        super().__init__()
        self.__is_alive = True


    def start_displaying(self):
        get_game().overworld.spawn(self)


    def stop_displaying(self):
        self.kill()


    def is_alive(self):
        return self.__is_alive


    def kill(self):
        self.__is_alive = False


    def get_choices(self):
        return ['Yes', 'No']


async def main(*args, **kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_1_canteen/vendors/1'))
    menu = ShopMenu()
    choice = await menu.choose()
    # TODO: actually buy the item
    get_game().overworld.unfreeze()
