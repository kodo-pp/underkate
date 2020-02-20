from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import wait_for_event, next_frame, wait_for_event_by_filter, notify_after
from underkate.sprite import BaseSprite
from underkate.text import draw_text
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.util import clamp
from underkate.vector import Vector, MappingFunction, Mappings

from abc import abstractmethod
from copy import copy
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


    def get_title(self):
        return ['']


    def get_coords_for_line(self, index):
        return (200, 400 + 40 * index)


    def get_coords_for_title(self, index):
        return (170, 350 + 40 * index)


    def get_coords_for_pointer(self, index):
        x, y = self.get_coords_for_line(index)
        return (x - 30, y + 10)


    def get_rect(self):
        return pg.Rect(140, 380, 200, 40 * len(self.get_choices()) + 20)


    def get_fill_color(self):
        return (0, 0, 0)


    def draw(self, destination):
        pg.draw.rect(destination, self.get_fill_color(), self.get_rect())
        for i, title_line in enumerate(self.get_title()):
            x, y = self.get_coords_for_title(i)
            draw_text(title_line, font=self.font, x=x, y=y, destination=destination)
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
    def __init__(self):
        super().__init__()
        self.__is_alive = True


    def start_displaying(self):
        get_game().overworld.spawn(self)


    def stop_displaying(self):
        self.kill()


    def is_alive(self):
        return self.__is_alive


    def kill(self):
        self.__is_alive = False


    def get_rect(self):
        return pg.Rect(150, 150, 500, 250)


    def get_coords_for_title(self, index):
        return (160, 180 + 40 * index)


    def get_coords_for_line(self, index):
        return (200, 220 + 40 * (index + len(self.get_title()) - 1))


class FightMixin:
    def __init__(self, fight_script, *args, **kwargs):
        self.fight_script = fight_script
        super().__init__(*args, **kwargs)


    def start_displaying(self):
        self.fight_script.element = self


    def stop_displaying(self):
        self.fight_script.element = None


class Menu(FightMixin, BaseMenu):
    pass



class MovementState:
    def __init__(self, coords: Vector, movement_length: float, mapping: MappingFunction):
        self.old_coords = copy(coords)
        self.new_coords = copy(coords)
        self.movement_length = movement_length
        self.elapsed_time: float = 0.0
        self.mapping = mapping


    def update(self, time_delta: float):
        self.elapsed_time += time_delta


    def get_current_coords(self) -> Vector:
        k = clamp(self.elapsed_time / self.movement_length, 0.0, 1.0)
        return self.old_coords.interpolated(self.new_coords, k, self.mapping)


    def move_to(self, new_coords: Vector):
        self.old_coords = self.get_current_coords()
        self.new_coords = new_coords
        self.elapsed_time = 0.0


class BulletBoard(FightMixin, BaseSprite):
    def __init__(self, fight_script):
        super().__init__(fight_script)
        self.board_texture = load_texture(Path('.') / 'assets' / 'fight' / 'bullet_board.png')
        self.heart_texture = load_texture(Path('.') / 'assets' / 'fight' / 'heart.png')
        self.row = 4
        self.col = 4
        self.movement_state = MovementState(
            coords = self.get_coords_at(self.row, self.col),
            movement_length = 0.15,
            mapping = Mappings.ease_out,
        )


    def update(self, time_delta: float):
        self.movement_state.update(time_delta)


    async def run(self, duration: float):
        time_up_event = get_event_manager().unique_id()
        notify_after(duration, time_up_event)
        while True:
            event, arg = await wait_for_event_by_filter(
                lambda event, arg: (event in [time_up_event, 'key:any'])
            )
            if event == time_up_event:
                break

            assert event == 'key:any'
            if arg.key == pg.K_UP:
                self.move(0, -1)
            elif arg.key == pg.K_DOWN:
                self.move(0, 1)
            elif arg.key == pg.K_LEFT:
                self.move(-1, 0)
            elif arg.key == pg.K_RIGHT:
                self.move(1, 0)


    def move(self, dx, dy):
        self.row = clamp(self.row + dy, 0, self.rows)
        self.col = clamp(self.col + dx, 0, self.cols)
        self.movement_state.move_to(self.get_coords_at(self.row, self.col))


    def draw(self, destination):
        center_x, center_y = self.center.ints()
        self.board_texture.draw(destination, center_x, center_y)
        coords = self.get_current_coords()
        print(f'BulletBoard: draw: coords = {coords}')
        x, y = coords.ints()
        self.heart_texture.draw(destination, x, y)


    def get_current_coords(self) -> Vector:
        return self.movement_state.get_current_coords()


    def get_coords_at(self, row: int, col: int) -> Vector:
        top_left_x = self.center.x - self.col_width * self.cols / 2.0
        top_left_y = self.center.y - self.row_height * self.rows / 2.0
        requested_x = top_left_x + self.col_width * col
        requested_y = top_left_y + self.row_height * row
        return Vector(requested_x + self.col_width / 2, requested_y + self.row_height / 2)


    center = Vector(400, 300)
    rows = 10
    cols = 10
    col_width = 40
    row_height = 40
