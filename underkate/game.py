from . import player
from . import sprite

from typing import Tuple, Optional

import pygame as pg


class GameExited(BaseException):
    pass


class Game:
    def __init__(self, window_size: Tuple[int, int] = (800, 600), target_fps: int = 60):
        self.window_size = window_size
        self.target_fps = target_fps
        self._fill_with_defaults()


    def _fill_with_defaults(self):
        self.player: Optional[player.Player] = None
        self.clock: Optional[pg.time.Clock] = None
        self.sprites: List[sprite.Sprite] = []
        self.screen: pg.Surface = []


    def __enter__(self) -> 'Game':
        pg.init()
        pg.display.set_mode(self.window_size)
        self.screen = pg.display.get_surface()
        self.player = player.get_player()
        self.sprites.append(self.player)
        self.clock = pg.time.Clock()
        return self


    def __exit__(self, *args):
        pg.quit()
        self._fill_with_defaults()


    def update(self, time_delta: float):
        self.process_events()

        # Filter out dead sprites
        self.sprites = [sprite for sprite in self.sprites if sprite.is_alive()]

        # Update all alive sprites
        for sprite in self.sprites:
            sprite.update(time_delta)


    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise GameExited()


    def draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_sprites()
        pg.display.flip()


    def _draw_sprites(self):
        for sprite in self.sprites:
            sprite.draw(self.screen)


    def run(self):
        try:
            while True:
                time_delta = self.clock.tick(self.target_fps) / 1000.0
                self.update(time_delta)
                self.draw()
        except GameExited:
            return
