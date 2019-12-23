from .textured_walking_sprite import TexturedWalkingSprite
from .animation import load_animation
from .vector import Vector

from typing import Optional

import pygame as pg


class Player(TexturedWalkingSprite):
    def __init__(self, pos: Vector):
        super().__init__(
            pos = pos,
            left = load_animation('assets/player/left', 4),
            right = load_animation('assets/player/right', 4),
            front = load_animation('assets/player/front', 4),
            back = load_animation('assets/player/back', 4),
            speed = 160.0,
        )

    def update(self, time_delta: float):
        super().update(time_delta)
        pressed_keys = pg.key.get_pressed()
        x, y = 0, 0
        if pressed_keys[pg.K_LEFT]:
            x -= 1
        if pressed_keys[pg.K_RIGHT]:
            x += 1
        if pressed_keys[pg.K_UP]:
            y -= 1
        if pressed_keys[pg.K_DOWN]:
            y += 1
        self.set_moving(x, y)


_player: Optional[Player] = None


def get_player() -> Player:
    global _player

    if _player is None:
        _player = Player(pos=Vector(100, 100))
    return _player
