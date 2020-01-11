from .sprite import Sprite
from .texture import BaseTexture

from typing import Optional

import pygame as pg  # type: ignore


def generate_hitbox(width: int, height: int) -> pg.Rect:
    hitbox = pg.Rect(0, 0, width, height)
    hitbox.center = (0, 0)
    return hitbox


class Object(Sprite):
    def __init__(
        self,
        pos: Vector,
        texture: Optional[BaseTexture] = None,
        is_passable: bool = False,
        hitbox: Optional[pg.Rect] = None,
    ):
        super().__init__(self, pos)
        self.texture = texture
        self.is_passable = is_passable
        self.hitbox = hitbox if self.hitbox is not None else generate_hitbox(20, 20)

    def update(self):
        pass

    def draw(self, surface: pg.Surface):
        if self.texture is None:
            return
        x, y = self.pos.ints()
        self.texture.draw(surface, x, y)

    def can_player_pass(self, player_position: pg.Rect) -> bool:
        return bool(self.hitbox.colliderect(player_position))