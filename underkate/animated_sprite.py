from .sprite import Sprite

import abc
import time

import pygame as pg  # type: ignore


class AnimatedSprite(Sprite):
    def __init__(self):
        self._start_time: float = 0.0
        self._has_started = False

    def start_animation(self):
        self._start_time = time.monotonic()
        self._has_started = True
        self.on_start()
        return self

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def get_elapsed_time(self) -> float:
        current_time = time.monotonic()
        return current_time - self._start_time
    
    def draw(self, surface: pg.Surface):
        elapsed_time = self.get_elapsed_time()
        self.draw_frame(surface, elapsed_time)

    @abc.abstractmethod
    def draw_frame(self, surface: pg.Surface, elapsed_time: float):
        ...
    
    def has_animation_started(self) -> bool:
        return self._has_started

    @abc.abstractmethod
    def has_animation_finished(self) -> bool:
        ...

    def is_alive(self) -> bool:
        return not self.has_animation_finished()

    def on_kill(self):
        super().on_kill()
        self.on_stop()
