from underkate.sprite import Sprite
from underkate.texture import BaseTexture
from underkate.vector import Vector

import pygame as pg  # type: ignore


class TexturedSprite(Sprite):
    def __init__(self, pos: Vector, texture: BaseTexture):
        super().__init__(pos)
        self.texture = texture


    def draw(self, destination: pg.Surface):
        x, y = self.pos.ints()
        self.texture.draw(destination, x, y)
