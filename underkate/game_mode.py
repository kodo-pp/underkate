from underkate.event_manager import get_event_manager, Subscriber
from underkate.room_transition import RoomTransitionFadeIn, RoomTransitionFadeOut
from underkate.scriptlib.common import wait_for_event, make_callback
from underkate.sprite import BaseSprite
from underkate.wal_list import WalList

from typing import Callable, TYPE_CHECKING

import pygame as pg  # type: ignore

if TYPE_CHECKING:
    from underkate.game import Game


class GameMode:
    def __init__(self, game: 'Game'):
        self.game = game
        self.sprites: WalList[BaseSprite] = WalList([])


    def draw(self, destination: pg.Surface):
        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)


    def update(self, time_delta: float):
        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)
        self.sprites.filter(lambda x: x.is_alive(), deleter = lambda x: x.on_kill())


    def spawn(self, sprite: BaseSprite):
        self.sprites.append(sprite)


    def show(self, on_finish: Callable):
        self.spawn(RoomTransitionFadeOut(self.game.screen.get_size()).start_animation())
        get_event_manager().subscribe(
            'room_enter_animation_finished',
            Subscriber(lambda event_id, arg: on_finish()),
        )


    def hide(self, on_finish: Callable):
        self.spawn(RoomTransitionFadeIn(self.game.screen.get_size()).start_animation())
        get_event_manager().subscribe(
            'room_exit_animation_finished',
            Subscriber(lambda event_id, arg: on_finish()),
        )


    async def async_show(self):
        event_id, callback = make_callback()
        self.show(callback)
        await wait_for_event(event_id)


    async def async_hide(self):
        event_id, callback = make_callback()
        self.hide(callback)
        await wait_for_event(event_id)
