from underkate.animated_sprite import AnimatedSprite
from underkate.texture import load_texture
from underkate.util import clamp

from pathlib import Path

import pygame as pg


class FightEnterAnimation(AnimatedSprite):
    def __init__(self, narrow_down_length, remain_length, pos, initial_scale):
        self.narrow_down_length = narrow_down_length
        self.remain_length = remain_length
        self.pos = pos
        self.initial_scale = initial_scale
        self.texture = load_texture(Path('.') / 'assets' / 'textures' / 'fight_warning.png')


    def calculate_scale(self, elapsed_time):
        return clamp(
            (self.initial_scale - 1.0) * (1.0 - elapsed_time / self.narrow_down_length),
            1.0,
            self.initial_scale,
        )


    def calculate_alpha(self, elapsed_time):
        return clamp(
            int(round(elapsed_time / self.narrow_down_length * 255)),
            0,
            255,
        )


    def draw_frame(self, surface, elapsed_time):
        scale = self.calculate_scale(elapsed_time)
        orig_w = self.texture.get_width()
        orig_h = self.texture.get_height()
        new_w = int(round(orig_w * scale))
        new_h = int(round(orig_h * scale))
        scaled_image = pg.transform.smoothscale(self.texture.image, (new_w, new_h))
        destination = scaled_image.get_rect()
        destination.center = self.pos.ints()

        mask = pg.Surface(scaled_image.get_size(), pg.SRCALPHA)
        mask.fill((255, 255, 255, self.calculate_alpha(elapsed_time)))
        scaled_image.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        surface.blit(scaled_image, destination)


    def has_animation_finished(self):
        return self.get_elapsed_time() >= self.narrow_down_length + self.remain_length
