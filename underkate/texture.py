import pygame # type: ignore
import pygame.image # type: ignore

import abc
from pathlib import Path
from typing import Union


class BaseTexture:
    @abc.abstractmethod
    def draw(self, surface: pygame.Surface, x: int, y: int):
        pass


class Texture(BaseTexture):
    def __init__(self, image: pygame.Surface, scale: int = 1):
        new_width = image.get_width() * scale
        new_height = image.get_height() * scale
        self.image = pygame.transform.scale(image, (new_width, new_height))

    def draw(self, surface: pygame.Surface, x: int, y: int):
        destination = self.image.get_rect()
        destination.center = (x, y)
        surface.blit(self.image, destination)


def load_texture(path: Union[Path, str], scale: int = 1) -> Texture:
    if isinstance(path, str):
        path = Path(path)
    
    with path.open() as f:
        return Texture(pygame.image.load(f), scale)
