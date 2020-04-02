from underkate import save_file
from underkate.game_mode import GameMode
from underkate.script import SimpleScript
from underkate.scriptlib.ui import BaseMenu

from typing import TYPE_CHECKING

import pygame as pg  # type: ignore

if TYPE_CHECKING:
    from underkate.game import Game


class Play:
    def __str__(self):
        return 'Play'


    async def perform_action(self, game):
        save_file.load(game)


class Reset:
    def __str__(self):
        return 'Reset'


    async def perform_action(self, game):
        save_file.delete()
        save_file.load(game)


class MainMenuUi(BaseMenu):
    def __init__(self, main_menu_mode):
        self.main_menu_mode = main_menu_mode


    def start_displaying(self):
        self.main_menu_mode.element = self


    def stop_displaying(self):
        self.main_menu_mode.element = None


    def get_choices(self):
        return [Play(), Reset()]


    def get_border_width(self):
        return 0


class MainMenuMode(GameMode):
    def __init__(self, game: 'Game'):
        super().__init__(game)
        self.menu = MainMenuUi(self)
        self.element = None
        script = SimpleScript(self.run)
        script()


    async def run(self, **kwargs):
        del kwargs
        choice = await self.menu.choose()
        await choice.perform_action(self.game)


    def draw(self, destination: pg.Surface):
        super().draw(destination)
        if self.element is not None:
            self.element.draw(destination)
