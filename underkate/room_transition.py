from underkate.animated_sprite import AnimatedSprite
from underkate.event_manager import get_event_manager
from underkate.util import clamp

import abc
from typing import Tuple

import pygame as pg  # type: ignore


class RoomTransitionBase(AnimatedSprite):
    def __init__(self, size: Tuple[int, int], length = 0.35):
        super().__init__()
        self.length = length
        self.surface = pg.Surface(size)
        self.surface = self.surface.convert_alpha()


    def update(self, time_delta: float):
        pass


    def has_animation_finished(self):
        value = self.get_elapsed_time() > self.length
        return value


    @abc.abstractmethod
    def calculate_alpha_coefficient(self, elapsed_time: float) -> float:
        ...


    def draw_frame(self, surface: pg.Surface, elapsed_time: float):
        alpha_coefficient = self.calculate_alpha_coefficient(elapsed_time)
        alpha = int(round(alpha_coefficient * 255))
        self.surface.fill((0, 0, 0, alpha))
        surface.blit(self.surface, surface.get_rect())


    def is_osd(self):
        return True


class RoomTransitionFadeIn(RoomTransitionBase):
    def on_start(self):
        get_event_manager().raise_event('room_exit_animation_started', None)


    def on_stop(self):
        get_event_manager().raise_event('room_exit_animation_finished', None)


    def calculate_alpha_coefficient(self, elapsed_time: float) -> float:
        return clamp(elapsed_time / self.length, 0.0, 1.0)


    def is_osd(self):
        return True


class RoomTransitionFadeOut(RoomTransitionBase):
    def on_start(self):
        get_event_manager().raise_event('room_enter_animation_started', None)


    def on_stop(self):
        get_event_manager().raise_event('room_enter_animation_finished', None)


    def calculate_alpha_coefficient(self, elapsed_time: float) -> float:
        return 1.0 - clamp(elapsed_time / self.length, 0.0, 1.0)


    def is_osd(self):
        return True
