from underkate.counter import Counter
from underkate.event_manager import get_event_manager, Subscriber
from underkate.game_mode import GameMode
from underkate.overworld.load_room import load_room
from underkate.overworld.room import Room
from underkate.room_transition import RoomTransitionFadeIn, RoomTransitionFadeOut
from underkate.sprite import Sprite
from underkate.vector import Vector

from pathlib import Path
from typing import List, TYPE_CHECKING

import pygame as pg  # type: ignore
from loguru import logger

if TYPE_CHECKING:
    from underkate.game import Game


class Overworld(GameMode):
    def __init__(self, game: 'Game'):
        super().__init__(game)
        self._room_loaded = False
        self._frozen = Counter()
        self.freeze()
        self.room: Room
        self._room_screen: pg.Surface
        self._run_room_loading_logic('start')


    def _run_room_loading_logic(self, room_name: str):
        if self._room_loaded:
            prev_room_name = self.room.name
        else:
            prev_room_name = 'default'

        self.room = load_room(Path('.') / 'assets' / 'rooms' / room_name, prev_room_name)
        self._room_screen = pg.Surface(self.room.get_size())
        self.spawn(RoomTransitionFadeOut(self.game.screen.get_size()).start_animation())
        subscriber = Subscriber(lambda event_id, arg: self._finalize_room_loading(room_name))
        get_event_manager().subscribe('room_enter_animation_finished', subscriber)


    def _finalize_room_loading(self, room_name: str):
        self.unfreeze()
        self._room_loaded = True
        self.room.maybe_run_script('on_load')


    def load_room(self, room_name: str):
        logger.debug('Loading room {}', room_name)
        self._room_ready = False
        self.freeze()
        self.spawn(RoomTransitionFadeIn(self.game.screen.get_size()).start_animation())
        get_event_manager().subscribe(
            'room_exit_animation_finished',
            Subscriber(lambda event_id, arg: self._run_room_loading_logic(room_name)),
        )


    def _get_view_rect(self) -> pg.Rect:
        width, height = self.room.get_size()
        x, y = self.room.player.pos.ints()
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


    def draw(self, destination: pg.Surface):
        self._room_screen.set_clip(self._get_view_rect())
        self._room_screen.fill((0, 0, 0))
        self.room.draw(self._room_screen)
        self._blit_scrolled_screen(destination)
        super().draw(destination)


    def _blit_scrolled_screen(self, destination: pg.Surface):
        rect = self._get_view_rect()
        destination.blit(self._room_screen, self._room_screen.get_rect(), rect)


    def update(self, time_delta: float):
        self.room.update(time_delta)
        super().update(time_delta)


    def freeze(self):
        self._frozen.increase()


    def unfreeze(self):
        self._frozen.decrease()


    def is_frozen(self) -> bool:
        return not self._frozen.is_zero()
