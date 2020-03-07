from underkate.texture import BaseTexture, load_texture

import time
from pathlib import Path
from typing import List, Union, Callable, Tuple

import pygame as pg  # type: ignore
import yaml


class AnimatedOnceTexture(BaseTexture):
    def __init__(self, frames: List[BaseTexture], delay: float, on_finish: Callable = lambda: None):
        self.frames = frames
        self.delay = delay
        self.start_time = time.monotonic()
        self._has_finished = False
        self.on_finish = on_finish


    def get_frame_info(self) -> Tuple[int, bool]:
        now = time.monotonic()
        time_delta = now - self.start_time
        raw_frame_num = int(time_delta // self.delay)
        clamped_frame_num = min(raw_frame_num, len(self.frames) - 1)
        has_finished = raw_frame_num > clamped_frame_num
        return clamped_frame_num, has_finished


    def draw(self, surface: pg.Surface, x: int, y: int):
        frame_num, has_finished = self.get_frame_info()
        if has_finished and not self._has_finished:
            self._has_finished = True
            self.on_finish()
        self.frames[frame_num].draw(surface, x, y)


    def get_width(self):
        return self.frames[0].get_width()


    def get_height(self):
        return self.frames[0].get_height()


    def clipped(self, clip_rect: pg.Rect):
        raise NotImplementedError()


def load_animated_once_texture(path: Union[Path, str], scale: int = 1) -> AnimatedOnceTexture:
    if isinstance(path, str):
        path = Path(path)

    config_path = path / 'animation.yml'
    with open(config_path) as f:
        data = yaml.safe_load(f)

    frames: List[BaseTexture] = []
    for frame_filename in data['frames']:
        frames.append(load_texture(path / frame_filename, scale))

    delay = data['delay']
    return AnimatedOnceTexture(frames, delay)
