from underkate import font
from underkate import player
from underkate import room
from underkate import text
from underkate import vector
from underkate.event_manager import get_event_manager, Subscriber
from underkate.game_singletone import set_game
from underkate.pending_callback_queue import get_pending_callback_queue
from underkate.room_transition import RoomTransitionFadeIn, RoomTransitionFadeOut
from underkate.sprite import Sprite

from pathlib import Path
from typing import Tuple, Optional, List, cast

import pygame as pg # type: ignore
from loguru import logger


class GameExited(BaseException):
    pass


class Game:
    def __init__(self, window_size: Tuple[int, int] = (800, 600), target_fps: int = 60):
        # Initialize singletone
        set_game(self)

        # Save parameters
        self.window_size = window_size
        self.target_fps = target_fps

        # Initialize PyGame
        pg.init()
        pg.display.set_mode(self.window_size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.screen = pg.display.get_surface()
        self._should_draw = True

        # Initialize clock
        self.clock = pg.time.Clock()

        # Initialize player
        self.player = player.Player(vector.Vector(100, 100), self)
        self.sprites: List[Sprite] = [self.player]
        self._sprite_queue: List[Sprite] = []

        self.room_loaded = False
        self.room: room.Room

        self.font = font.load_font(Path('.') / 'assets' / 'fonts' / 'default')

        # Load starting room
        self.player.disable_controls()
        self._run_room_loading_logic('start')

        # Initialize FPS counter
        get_pending_callback_queue().fire_after(1.0, self._print_fps)


    def __enter__(self) -> 'Game':
        return self


    def __exit__(self, *args):
        pg.quit()


    def _print_fps(self):
        logger.debug('FPS: {}', self.clock.get_fps())
        get_pending_callback_queue().fire_after(1.0, self._print_fps)


    def _run_room_loading_logic(self, room_name: str):
        logger.debug('Game._run_room_loading_logic({})', room_name)
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
        self.spawn(RoomTransitionFadeOut(self.screen.get_size(), self).start_animation())
        subscriber = Subscriber(lambda event_id, arg: self._finalize_room_loading(room_name))
        get_event_manager().subscribe('room_enter_animation_finished', subscriber)


    def _finalize_room_loading(self, room_name: str):
        logger.debug('Game._finalize_room_loading({})', room_name)
        self.player.restore_controls()
        self.room.on_load()


    def load_room(self, room_name: str):
        logger.debug('Game.load_room({})', room_name)
        self.player.disable_controls()
        self.spawn(RoomTransitionFadeIn(self.screen.get_size(), self).start_animation())
        get_event_manager().subscribe(
            'room_exit_animation_finished',
            Subscriber(lambda event_id, arg: self._run_room_loading_logic(room_name)),
        )


    def disable_drawing(self):
        self._should_draw = False


    def enable_drawing(self):
        self._should_draw = True


    def update(self, time_delta: float):
        self.process_events()

        # Filter out dead sprites
        dead_sprites = [sprite for sprite in self.sprites if not sprite.is_alive()]
        for sprite in dead_sprites:
            sprite.on_kill()
        self.sprites = [sprite for sprite in self.sprites if sprite.is_alive()]
        if dead_sprites:
            logger.debug('Removed {} sprites', len(dead_sprites))

        # Add spawned sprites
        self.sprites += self._sprite_queue
        if self._sprite_queue:
            logger.debug('Spawned {} sprites', len(self._sprite_queue))
        self._sprite_queue = []

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
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_z, pg.K_RETURN):
                    get_event_manager().raise_event('key:confirm', event)
                elif event.key in (pg.K_x, pg.K_LSHIFT, pg.K_RSHIFT):
                    get_event_manager().raise_event('key:cancel', event)
                elif event.key in (pg.K_c, pg.K_LCTRL, pg.K_RCTRL):
                    get_event_manager().raise_event('key:menu', event)


    def spawn(self, sprite: Sprite):
        self._sprite_queue.append(sprite)


    def draw(self):
        self.room_screen.set_clip(self.get_view_rect())
        self.room_screen.fill((0, 0, 0))
        if self._should_draw:
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
        sprites_drawn = 0
        for sprite in self.sprites:
            if sprite.is_osd():
                sprite.draw(self.screen)
                sprites_drawn += 1
        if sprites_drawn > 1:
            logger.trace('Drew {} OSD sprites', sprites_drawn)


    def run(self):
        try:
            while True:
                time_delta = self.clock.tick(self.target_fps) / 1000.0
                self.update(time_delta)
                self.draw()
        except GameExited:
            return
