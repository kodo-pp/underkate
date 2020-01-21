from underkate.event_manager import get_event_manager
from underkate.game_mode import GameMode
from underkate.global_game import set_game
from underkate.overworld.mode import Overworld
from underkate.pending_callback_queue import get_pending_callback_queue

from typing import Tuple

import pygame as pg # type: ignore
from loguru import logger


class GameExited(BaseException):
    pass


class Game:
    def __init__(self, window_size: Tuple[int, int] = (800, 600), target_fps: int = 60):
        # Initialize the global `game` object
        set_game(self)

        # Save parameters
        self.window_size = window_size
        self.target_fps = target_fps

        # Initialize PyGame
        pg.init()
        pg.display.set_mode(self.window_size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.screen = pg.display.get_surface()

        # Initialize clock
        self.clock = pg.time.Clock()

        # Initialize FPS counter
        get_pending_callback_queue().fire_after(1.0, self._print_fps)

        # Initialize game modes
        self.overworld = Overworld(self)
        self.current_game_mode: GameMode = self.overworld


    def __enter__(self) -> 'Game':
        return self


    def __exit__(self, *args):
        pg.quit()


    def _print_fps(self):
        # Print FPS and schedule the next call to this function in one second
        logger.debug('FPS: {}', self.clock.get_fps())
        get_pending_callback_queue().fire_after(1.0, self._print_fps)


    def update(self, time_delta: float):
        # Handle events that occured since last check
        self.process_events()

        # Run scheduled callbacks
        get_pending_callback_queue().update()

        # Delegate the main update logic to the current game mode
        self.current_game_mode.update(time_delta)

        # Finalize the update cycle
        get_event_manager().raise_event('end_of_cycle', None)


    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise GameExited()
            if event.type == pg.KEYDOWN:
                # Process special keys
                if event.key in (pg.K_z, pg.K_RETURN):
                    get_event_manager().raise_event('key:confirm', event)
                elif event.key in (pg.K_x, pg.K_LSHIFT, pg.K_RSHIFT):
                    get_event_manager().raise_event('key:cancel', event)
                elif event.key in (pg.K_c, pg.K_LCTRL, pg.K_RCTRL):
                    get_event_manager().raise_event('key:menu', event)


    def draw(self):
        self.screen.fill((0, 0, 0))
        self.current_game_mode.draw(self.screen)
        pg.display.flip()


    def run(self):
        try:
            while True:
                time_delta: float = self.clock.tick(self.target_fps) / 1000.0
                self.update(time_delta)
                self.draw()
        except GameExited:
            return
