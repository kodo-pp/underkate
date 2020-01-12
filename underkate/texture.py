import pygame # type: ignore
import pygame.image # type: ignore

import abc
from pathlib import Path
from typing import Union

from loguru import logger


class BaseTexture:
    @abc.abstractmethod
    def draw(self, surface: pygame.Surface, x: int, y: int):
        pass


class Texture(BaseTexture):
    def __init__(self, image: pygame.Surface, scale: int = 1, force_software: bool = False):
        new_width = image.get_width() * scale
        new_height = image.get_height() * scale
        sw_image = pygame.transform.scale(image, (new_width, new_height))
        if force_software:
            self.image = sw_image
        else:
            self.image = pygame.Surface(sw_image.get_size(), pygame.HWSURFACE | pygame.SRCALPHA, 32)
            self.image.fill((0,0,0,0))
            self.image.blit(sw_image, self.image.get_rect())


    def draw(self, surface: pygame.Surface, x: int, y: int):
        destination = self.image.get_rect()
        destination.center = (x, y)
        surface.blit(self.image, destination)


def load_texture(path: Union[Path, str], scale: int = 1) -> Texture:
    logger.info('Loading texture: {}', path)
    if isinstance(path, str):
        path = Path(path)

    with path.open() as f:
        return Texture(pygame.image.load(f), scale)
