from underkate.event_manager import get_event_manager
from underkate.fight.mode import Fight
from underkate.game_mode import GameMode
from underkate.global_game import set_game
from underkate.main_menu.mode import MainMenuMode
from underkate.overworld.mode import Overworld
from underkate.pending_callback_queue import get_pending_callback_queue
from underkate.script import SuspendedPythonScript

from typing import Tuple, Optional, List

import pygame as pg # type: ignore
from loguru import logger


class GameExited(BaseException):
    pass


class Game:
    def __init__(self, window_size: Tuple[int, int] = (800, 600), target_fps: int = 60):
        # Initialize the global `game` object
        set_game(self)

        # Initialize coroutine support in scripts
        self._current_script_stack: List[SuspendedPythonScript] = []

        # Save parameters
        self.window_size = window_size
        self.target_fps = target_fps

        # Initialize PyGame
        pg.init()
        pg.display.set_mode(self.window_size, pg.HWSURFACE | pg.DOUBLEBUF)
        pg.display.set_caption('Underkate')
        pg.display.set_icon(pg.image.load('assets/icon.png'))
        self.screen = pg.display.get_surface()

        # Initialize clock
        self.clock = pg.time.Clock()

        # Initialize FPS counter
        get_pending_callback_queue().fire_after(1.0, self._print_fps)

        # Initialize game modes
        self.overworld = Overworld(self)
        self.fight: Optional[Fight] = None
        #self.current_game_mode: GameMode = self.overworld
        self.current_game_mode: GameMode = MainMenuMode(self)



    @property
    def current_script(self):
        return self._current_script_stack[-1]


    def push_current_script(self, script: SuspendedPythonScript):
        self._current_script_stack.append(script)


    def pop_current_script(self):
        self._current_script_stack.pop()


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
        get_event_manager().raise_event('end_of_cycle', None, silent=True)


    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise GameExited()
            if event.type == pg.KEYDOWN:
                # Process all keys
                get_event_manager().raise_event('key:any', event)

                # Process special keys
                if event.key in (pg.K_z, pg.K_RETURN):
                    get_event_manager().raise_event('key:confirm', event)
                if event.key in (pg.K_x, pg.K_LSHIFT, pg.K_RSHIFT):
                    get_event_manager().raise_event('key:cancel', event)
                if event.key in (pg.K_c, pg.K_LCTRL, pg.K_RCTRL):
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
