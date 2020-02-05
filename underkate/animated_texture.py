from underkate.texture import BaseTexture, load_texture, Texture

import time
from pathlib import Path
from typing import List, Union, Optional

import pygame as pg  # type: ignore
import yaml


class AnimatedTexture(BaseTexture):
    def __init__(self, frames: List[BaseTexture], fps: int):
        self.frames = frames
        self.fps = fps


    def draw(self, surface: pg.Surface, x: int, y: int, force_frame: Optional[int] = None):
        now = time.time()
        if force_frame is not None:
            frame_num = force_frame
        else:
            frame_num = int(now * self.fps) % len(self.frames)
        self.frames[frame_num].draw(surface, x, y)


    def get_width(self):
        return self.frames[0].get_width()


    def get_height(self):
        return self.frames[0].get_height()


    def to_static(self) -> Texture:
        return Texture(self.frames[0])


    def clipped(self, clip_rect: pg.Rect) -> 'AnimatedTexture':
        frames = [frame.clipped(clip_rect) for frame in self.frames]
        return AnimatedTexture(frames, self.fps)


def load_animated_texture(path: Union[Path, str], scale: int = 1) -> AnimatedTexture:
    if isinstance(path, str):
        path = Path(path)

    config_path = path / 'animation.yml'
    with open(config_path) as f:
        config = yaml.safe_load(f)

    frames: List[BaseTexture] = []
    for frame_filename in config['frames']:
        frames.append(load_texture(path / frame_filename, scale))

    fps = config['fps']
    return AnimatedTexture(frames, fps)
