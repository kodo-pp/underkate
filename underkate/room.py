from .pass_map import PassMap
from .texture import BaseTexture, load_texture

from pathlib import Path
from typing import Union, cast

import pygame as pg
import yaml


class Room:
    def __init__(self, background: BaseTexture, pass_map: PassMap):
        self.background = background
        self.pass_map = pass_map

    def draw(self, surface: pg.Surface):
        x, y = surface.get_rect().center
        self.background.draw(surface, x, y)

    def is_passable(self, rect: pg.Rect) -> bool:
        return self.pass_map.is_passable(rect)


def load_room(path: Union[Path, str]) -> Room:
    if isinstance(path, str):
        path = Path(path)

    with open(path / 'room.yml') as f:
        data = yaml.safe_load(f)

    background_filename = path / cast(str, data['background'])
    pass_map_filename = path / cast(str, data['pass_map'])
    background = load_texture(background_filename)
    pass_map = PassMap(pg.image.load(str(pass_map_filename)))
    return Room(background, pass_map)
