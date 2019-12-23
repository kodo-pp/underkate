from . import player
from . import room
from . import sprite
from . import vector

from pathlib import Path
from typing import Tuple, Optional, List

import pygame as pg


class GameExited(BaseException):
    pass


class Game:
    def __init__(self, window_size: Tuple[int, int] = (800, 600), target_fps: int = 60):
        # Save parameters
        self.window_size = window_size
        self.target_fps = target_fps

        # Initialize PyGame
        pg.init()
        pg.display.set_mode(self.window_size)
        self.screen = pg.display.get_surface()

        # Initialize clock
        self.clock = pg.time.Clock()

        # Initialize player
        self.player = player.Player(vector.Vector(100, 100), self)
        self.sprites: List[sprite.Sprite] = [self.player]

        # Load starting room
        self.load_room('start')


    def __enter__(self) -> 'Game':
        return self


    def __exit__(self, *args):
        pg.quit()


    def load_room(self, room_name: str):
        self.room = room.load_room(Path('.') / 'assets' / 'rooms' / room_name)


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
        self.room.draw(self.screen)
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
