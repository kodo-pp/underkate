from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import wait_for_event, next_frame
from underkate.sprite import BaseSprite
from underkate.text import draw_text
from underkate.texture import load_texture

from abc import abstractmethod
from pathlib import Path

import pygame as pg  # type: ignore


class BaseMenu(BaseSprite):
    async def choose(self):
        self.index = 0
        self.font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        self.choices = self.get_choices()
        self.pointer_texture = load_texture(Path('.') / 'assets' / 'fight' / 'pointer.png', scale=2)
        self.start_displaying()
        while True:
            _, pygame_event = await wait_for_event('key:any')
            key = pygame_event.key
            if key == pg.K_UP:
                self.on_key_up()
            if key == pg.K_DOWN:
                self.on_key_down()
            if key in (pg.K_z, pg.K_RETURN, pg.K_LSHIFT, pg.K_RSHIFT):
                break
        choice = self.choices[self.index]
        self.stop_displaying()
        await next_frame()
        return choice


    def get_coords_for_line(self, index):
        return (200, 400 + 40 * index)


    def get_coords_for_pointer(self, index):
        x, y = self.get_coords_for_line(index)
        return (x - 30, y + 10)


    def get_rect(self):
        return pg.Rect(140, 380, 200, 40 * len(self.get_choices()) + 20)


    def get_fill_color(self):
        return (0, 0, 0)


    def draw(self, destination):
        pg.draw.rect(destination, self.get_fill_color(), self.get_rect())
        for i, choice in enumerate(self.choices):
            x, y = self.get_coords_for_line(i)
            draw_text(str(choice), font=self.font, x=x, y=y, destination=destination)
        x, y = self.get_coords_for_pointer(self.index)
        self.pointer_texture.draw(destination, x=x, y=y)


    def update(self, time_delta):
        pass


    def on_key_up(self):
        self.index = max(self.index - 1, 0)


    def on_key_down(self):
        self.index = min(self.index + 1, len(self.choices) - 1)


    @abstractmethod
    def get_choices(self):
        ...


    @abstractmethod
    def start_displaying(self):
        ...


    @abstractmethod
    def stop_displaying(self):
        ...


class OverworldMenu(BaseMenu):
    def get_rect(self):
        return pg.Rect(250, 150, 300, 250)


    def get_coords_for_line(self, index):
        return (300, 200 + 40 * index)


class Menu(BaseMenu):
    def __init__(self, fight_script):
        self.fight_script = fight_script


    def start_displaying(self):
        self.fight_script.element = self


    def stop_displaying(self):
        self.fight_script.element = None


class BulletBoard:
    def __init__(self, fight_script):
        self.fight_script = fight_script
        self.board_texture = load_texture(Path('.') / 'assets' / 'textures' / 'bullet_board.png')
        self.brain = load_texture(Path('.') / 'assets' / 'textures' / 'brain.png')
        self.x = 4
        self.y = 4

    # TODO
