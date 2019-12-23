from .animation import load_animation
from .pass_map import PassMap
from .textured_walking_sprite import TexturedWalkingSprite
from .vector import Vector

from typing import Optional

import pygame as pg


class Player(TexturedWalkingSprite):
    def __init__(self, pos: Vector, game: 'typing go fuck yourself please'):
        super().__init__(
            pos = pos,
            left = load_animation('assets/player/left', 4),
            right = load_animation('assets/player/right', 4),
            front = load_animation('assets/player/front', 4),
            back = load_animation('assets/player/back', 4),
            speed = 160.0,
        )
        self.game = game

    @staticmethod
    def get_hitbox():
        return pg.Rect(0, 0, 14 * 4, 18 * 4)

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
    
    def move(self, delta):
        result = self.pos + delta
        rect = self.get_hitbox()
        rect.center = result.ints()
        pass_map = self.game.room.pass_map
        if pass_map.is_passable(rect):
            super().move(delta)
