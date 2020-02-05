import abc
from pathlib import Path
from typing import Union

from abc import abstractmethod

import pygame as pg  # type: ignore
from loguru import logger
from memoization import cached  # type: ignore


class BaseTexture:
    @abc.abstractmethod
    def draw(self, surface: pg.Surface, x: int, y: int):
        ...


    def please_draw(self, surface: pg.Surface):
        self.draw(surface, self.get_width() // 2, self.get_height() // 2)


    @abc.abstractmethod
    def get_width(self):
        ...


    @abc.abstractmethod
    def get_height(self):
        ...


    def get_rect(self):
        return pg.Rect(0, 0, self.get_width(), self.get_height())


    def to_static(self) -> 'BaseTexture':
        return self


    @abstractmethod
    def clipped(self, clip_rect: pg.Rect) -> 'BaseTexture':
        ...



class Texture(BaseTexture):
    def __init__(self, image: pg.Surface, scale: int = 1, force_software: bool = False):
        new_width = image.get_width() * scale
        new_height = image.get_height() * scale
        sw_image = pg.transform.scale(image, (new_width, new_height))
        self._force_software = force_software
        if force_software:
            self.image = sw_image
        else:
            self.image = pg.Surface(sw_image.get_size(), pg.HWSURFACE | pg.SRCALPHA, 32)
            self.image.fill((0,0,0,0))
            self.image.blit(sw_image, self.image.get_rect())


    def draw(self, surface: pg.Surface, x: int, y: int):
        destination = self.image.get_rect()
        destination.center = (x, y)
        surface.blit(self.image, destination)


    def get_width(self):
        return self.image.get_width()


    def get_height(self):
        return self.image.get_height()


    def clipped(self, clip_rect: pg.Rect) -> 'Texture':
        return Texture(self.image.subsurface(clip_rect), 1, self._force_software)


@cached
def load_texture(path: Union[Path, str], scale: int = 1) -> Texture:
    logger.info('Loading texture: {}', path)
    if isinstance(path, str):
        path = Path(path)

    with path.open() as f:
        return Texture(pg.image.load(f), scale)
