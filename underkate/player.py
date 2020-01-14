from .animated_texture import load_animated_texture
from .counter import Counter
from .pass_map import PassMap
from .textured_walking_sprite import TexturedWalkingSprite
from .vector import Vector

from typing import Optional, TYPE_CHECKING, ContextManager

import pygame as pg # type: ignore

if TYPE_CHECKING:
    from .game import Game


class Player(TexturedWalkingSprite):
    def __init__(self, pos: Vector, game: 'Game'):
        super().__init__(
            pos = pos,
            left = load_animated_texture('assets/player/left', 4),
            right = load_animated_texture('assets/player/right', 4),
            front = load_animated_texture('assets/player/front', 4),
            back = load_animated_texture('assets/player/back', 4),
            speed = 250.0,
        )
        self.game = game
        self._controls_disabled_counter = Counter()


    @staticmethod
    def get_hitbox_for(pos: Vector) -> pg.Rect:
        x, y = pos.ints()
        return pg.Rect(x - 16, y + 4, 32, 32)


    @staticmethod
    def get_hitbox() -> pg.Rect:
        return pg.Rect(0, 40, 8 * 4, 8 * 4)


    def get_hitbox_with_position(self) -> pg.Rect:
        return self.get_hitbox_for(self.pos)


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

        if self.are_controls_disabled():
            x, y = 0, 0
        self.set_moving(x, y)


    def _can_move(self, delta: Vector) -> bool:
        if delta.is_zero():
            return True
        result = self.pos + delta
        rect = self.get_hitbox_for(result)
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


    def are_controls_disabled(self) -> bool:
        return not self._controls_disabled_counter.is_zero()


    def disable_controls(self):
        self._controls_disabled_counter.increase()


    def restore_controls(self):
        self._controls_disabled_counter.decrease()


    def with_controls_disabled(self) -> ContextManager[None]:
        return self._controls_disabled_counter.with_increased()
