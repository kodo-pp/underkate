from underkate import save_file
from underkate.game_mode import GameMode
from underkate.script import SimpleScript
from underkate.text import draw_text
from underkate.texture import load_texture

from pathlib import Path
from typing import TYPE_CHECKING

import pygame as pg  # type: ignore

if TYPE_CHECKING:
    from underkate.game import Game


class FinalScreenMode(GameMode):
    def __init__(self, game: 'Game'):
        super().__init__(game)
        self.logo = load_texture(Path('.') / 'assets' / 'textures' / 'logo.png', scale=12)
        self._elapsed_time = 0.0


    def draw(self, destination: pg.Surface):
        super().draw(destination)
        if self._elapsed_time >= 2.0:
            self.logo.draw(destination, 400, 100)
        if self._elapsed_time >= 5.0:
            draw_text('Chapter 1 completed', destination=destination, x=229, y=200)
        if self._elapsed_time >= 8.0:
            draw_text('More chapters will follow', destination=destination, x=175, y=300)
        if self._elapsed_time >= 11.0 and int(self._elapsed_time * 1.5) % 2 == 0:
            draw_text('Thank you for playing!', destination=destination, x=200, y=400)


    def update(self, time_delta):
        self._elapsed_time += time_delta
