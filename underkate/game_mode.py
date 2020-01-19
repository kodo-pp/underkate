from underkate.sprite import Sprite
from underkate.wal_list import WalList

import abc
from typing import List, TYPE_CHECKING

import pygame as pg  # type: ignore

if TYPE_CHECKING:
    from underkate.game import Game


class GameMode:
    def __init__(self, game: 'Game'):
        self.game = game
        self.sprites: WalList[Sprite] = WalList([])


    def draw(self, destination: pg.Surface):
        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)


    def update(self, time_delta: float):
        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)
        self.sprites.filter(lambda x: x.is_alive(), deleter = lambda x: x.on_kill())


    def spawn(self, sprite: Sprite):
        self.sprites.append(sprite)
