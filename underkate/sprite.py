from .vector import Vector

import abc

import pygame


# Not using pygame's sprite because it has inconvenient API for my purpose
class Sprite:
    def __init__(self, pos: Vector):
        self.pos = pos

    @abc.abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    @abc.abstractmethod
    def update(self, time_delta: float):
        pass

    def is_alive(self) -> bool:
        return True
