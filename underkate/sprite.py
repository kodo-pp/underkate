from underkate.vector import Vector

import abc

import pygame as pg  # type: ignore


class BaseSprite:
    def __init__(self):
        self._is_alive = True


    def is_alive(self) -> bool:
        return self._is_alive


    def kill(self):
        self._is_alive = False


    @abc.abstractmethod
    def draw(self, destination: pg.Surface):
        pass


    def update(self, time_delta: float):
        pass


    def is_osd(self) -> bool:
        return False


    def on_kill(self):
        pass


class Sprite(BaseSprite):
    def __init__(self, pos: Vector):
        super().__init__()
        self.pos = pos
