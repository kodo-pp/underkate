from underkate import save_file
from underkate.game_mode import GameMode
from underkate.script import SimpleScript
from underkate.scriptlib.common import sleep
from underkate.scriptlib.fight import DisappearAnimation
from underkate.state import get_state
from underkate.text import draw_text
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

from pathlib import Path
from typing import TYPE_CHECKING

import pygame as pg  # type: ignore

if TYPE_CHECKING:
    from underkate.game import Game


class DeathScreenMode(GameMode):
    def __init__(self, game: 'Game', heart_pos: Vector):
        super().__init__(game)
        self.heart_pos = heart_pos
        self._elapsed_time = None
        self._draw = self.draw_animation
        SimpleScript(self.run)()


    async def run(self, **kwargs):
        heart_texture = load_texture(Path('.') / 'assets' / 'fight' / 'heart.png', scale=1)
        sprite = TexturedSprite(pos=self.heart_pos, texture=heart_texture)
        self.spawn(sprite)
        await sleep(2)
        sprite.kill()
        await DisappearAnimation(pos=self.heart_pos, texture=heart_texture).animate()
        self._elapsed_time = 0.0
        await sleep(0.5)
        self.draw = self.draw_death_text


    def draw_animation(self, destination: pg.Surface):
        super().draw(destination)


    def draw(self, destination: pg.Surface):
        self._draw(destination)


    def draw_death_text(self, destination: pg.Surface):
        super().draw(destination)
        assert self._elapsed_time is not None
        n = int(self._elapsed_time * 15.0)
        draw_text('You have been expelled...'[:n], destination=destination, x=175, y=200)


    def update(self, time_delta):
        super().update(time_delta)
        if self._elapsed_time is not None:
            self._elapsed_time += time_delta
