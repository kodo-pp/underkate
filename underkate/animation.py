from .texture import BaseTexture, load_texture

import time
from pathlib import Path
from typing import List, Union, Optional

import pygame
import yaml


class Animation(BaseTexture):
    def __init__(self, frames: List[BaseTexture], fps: int):
        self.frames = frames
        self.fps = fps

    def draw(self, surface: pygame.Surface, x, y, force_frame: Optional[int] = None):
        now = time.time()
        if force_frame is not None:
            frame_num = force_frame
        else:
            frame_num = int(now * self.fps) % len(self.frames)
        self.frames[frame_num].draw(surface, x, y)


def load_animation(path: Union[Path, str], scale: int = 1) -> Animation:
    if isinstance(path, str):
        path = Path(path)

    config_path = path / 'animation.yml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    frames: List[BaseTexture] = []
    for frame_filename in config['frames']:
        frames.append(load_texture(path / frame_filename, scale))
    
    fps = config['fps']
    return Animation(frames, fps)
