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
    def get_hitbox() -> pg.Rect:
        return pg.Rect(0, 0, 14 * 4, 18 * 4)

    def get_hitbox_with_position(self) -> pg.Rect:
        hitbox = self.get_hitbox()
        hitbox.center = self.pos.ints()
        return hitbox

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
    
    def _can_move(self, delta: Vector) -> bool:
        result = self.pos + delta
        rect = self.get_hitbox()
        rect.center = result.ints()
        pass_map = self.game.room.pass_map
        return pass_map.is_passable(rect)

    def _move_unchecked(self, delta: Vector):
        super().move(delta)

    def move(self, delta: Vector):
        if self._can_move(delta):
            self._move_unchecked(delta)
            return

        eps = 1e-9
        if abs(delta.x) > eps and abs(delta.y) > eps:
            if self._can_move(Vector(delta.x, 0.0)):
                self._move_unchecked(Vector(delta.x, 0.0))
            elif self._can_move(Vector(0.0, delta.y)):
                self._move_unchecked(Vector(0.0, delta.y))
