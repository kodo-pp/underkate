from . import font
from . import player
from . import room
from . import sprite
from . import text
from . import vector
from .pending_callback_queue import get_pending_callback_queue

from pathlib import Path
from typing import Tuple, Optional, List, cast

import pygame as pg # type: ignore


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
    
        self.room_loaded = False
        self.room: room.Room

        self.font = font.load_font(Path('.') / 'assets' / 'fonts' / 'default')

        txt = text.DisplayedText([
            text.TextPage('A strange light fills the room, which is a test message intended to be long enough to cause a line break to occur naturally. However\nwe can also force it to appear', self.font),
            text.TextPage('Hello world!', self.font),
        ], self)
        self.sprites.append(txt)
        txt.initialize()

        # Load starting room
        self.load_room('start')


    def __enter__(self) -> 'Game':
        return self


    def __exit__(self, *args):
        pg.quit()


    def load_room(self, room_name: str, argument: str = ''):
        if self.room_loaded:
            prev_room_name = self.room.name
        else:
            prev_room_name = 'default'

        self.room = room.load_room(
            Path('.') / 'assets' / 'rooms' / room_name,
            game = self,
        )
        self.room_loaded = True
        self.player.pos = self.room.initial_positions[prev_room_name]
        self.room_screen = pg.Surface(self.room.get_size())
        self.room.on_load()


    def update(self, time_delta: float):
        self.process_events()

        # Filter out dead sprites
        self.sprites = [sprite for sprite in self.sprites if sprite.is_alive()]

        # Update all alive sprites
        for sprite in self.sprites:
            sprite.update(time_delta)

        # Update the room
        self.room.update(self.player)

        # Run callbacks
        get_pending_callback_queue().update()

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise GameExited()


    def draw(self):
        self.room_screen.fill((0, 0, 0))
        self.room.draw(self.room_screen)
        self._draw_non_osd_sprites()
        self._blit_scrolled_screen()
        self._draw_osd_sprites()
        pg.display.flip()


    def _blit_scrolled_screen(self):
        rect = self.get_view_rect()
        self.screen.blit(self.room_screen, self.room_screen.get_rect(), rect)


    def get_view_rect(self) -> pg.Rect:
        width, height = self.room.get_size()
        x, y = self.player.pos.ints()
        view_width, view_height = 800, 600

        if view_width >= width:
            offset_x = 0
        else:
            scrolled_width = max(0.0, width - view_width)
            half_view_width = 0.5 * view_width
            k_x = max(0.0, min(1.0, (x - half_view_width) / (width - view_width)))
            offset_x = int(round(scrolled_width * k_x))

        if view_height >= height:
            offset_y = 0
        else:
            scrolled_height = max(0.0, height - view_height)
            half_view_height = 0.5 * view_height
            k_y = max(0.0, min(1.0, (y - half_view_height) / (height - view_height)))
            offset_y = int(round(scrolled_height * k_y))

        return pg.Rect(offset_x, offset_y, offset_x + view_width, offset_y + view_height)


    def _draw_non_osd_sprites(self):
        for sprite in self.sprites:
            if not sprite.is_osd():
                sprite.draw(self.room_screen)


    def _draw_osd_sprites(self):
        for sprite in self.sprites:
            if sprite.is_osd():
                sprite.draw(self.screen)


    def run(self):
        try:
            while True:
                time_delta = self.clock.tick(self.target_fps) / 1000.0
                self.update(time_delta)
                self.draw()
        except GameExited:
            return
