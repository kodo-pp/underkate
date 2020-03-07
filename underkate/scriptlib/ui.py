from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import notify_after
from underkate.scriptlib.common import wait_for_event, next_frame, wait_for_event_by_filter
from underkate.sprite import BaseSprite
from underkate.state import get_state
from underkate.text import draw_text
from underkate.texture import load_texture
from underkate.util import clamp
from underkate.vector import Vector, MappingFunction, Mappings
from underkate.wal_list import WalList

import time
import sys
from abc import abstractmethod
from copy import copy
from pathlib import Path
from typing import Tuple, Optional, TYPE_CHECKING

import pygame as pg  # type: ignore
from loguru import logger

if TYPE_CHECKING:
    from underkate.scriptlib.fight import FightScript


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
    def __init__(self, fight_script: 'FightScript', *args, **kwargs):
        self.fight_script = fight_script
        # Mypy swears a lot about the next line without any obvious reason
        super().__init__(*args, **kwargs)  # type: ignore


    def start_displaying(self):
        self.fight_script.elements.append(self)


    def stop_displaying(self):
        self.fight_script.elements.filter(lambda x: x is not self)


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
    def __init__(self, fight_script: 'FightScript'):
        super().__init__(fight_script)
        self.board_texture = load_texture(Path('.') / 'assets' / 'fight' / 'bullet_board.png')
        self.heart_texture = load_texture(Path('.') / 'assets' / 'fight' / 'heart.png')
        self.hit_heart_texture = load_texture(Path('.') / 'assets' / 'fight' / 'hit_heart.png')
        self.row = 4
        self.col = 4
        self.movement_state = MovementState(
            coords = self.get_coords_at(self.row, self.col),
            movement_length = 0.15,
            mapping = Mappings.ease_out,
        )
        self.sprites: WalList[BaseSprite] = WalList([])
        self._last_time_player_hit: Optional[float] = None


    def spawn(self, sprite: BaseSprite):
        self.sprites.append(sprite)


    def update(self, time_delta: float):
        self.movement_state.update(time_delta)
        with self.sprites:
            for x in self.sprites:
                x.update(time_delta)
        self.sprites.filter(lambda x: x.is_alive())


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


    def move(self, dx: int, dy: int):
        self.row = clamp(self.row + dy, 0, self.rows)
        self.col = clamp(self.col + dx, 0, self.cols)
        self.movement_state.move_to(self.get_coords_at(self.row, self.col))


    def draw(self, destination: pg.Surface):
        center_x, center_y = self.center.ints()
        self.board_texture.draw(destination, center_x, center_y)
        coords = self.get_current_coords()
        x, y = coords.ints()

        prev_clip = destination.get_clip()
        destination.set_clip(self.get_rect())

        if self._can_hit_player():
            self.heart_texture.draw(destination, x, y)
        else:
            self.hit_heart_texture.draw(destination, x, y)

        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)
        destination.set_clip(prev_clip)


    def get_current_coords(self) -> Vector:
        return self.movement_state.get_current_coords()


    def get_coords_at(self, row: int, col: int) -> Vector:
        x, y = self.get_rect_at(row, col).center
        return Vector(x, y)


    def get_rect_at(self, row: int, col: int) -> pg.Rect:
        top_left_x = self.center.x - self.col_width * self.cols / 2.0
        top_left_y = self.center.y - self.row_height * self.rows / 2.0
        requested_x = top_left_x + self.col_width * col
        requested_y = top_left_y + self.row_height * row
        return pg.Rect(requested_x, requested_y, self.col_width, self.row_height)


    def get_rect(self) -> pg.Rect:
        rect = pg.Rect(0, 0, self.cols * self.col_width, self.rows * self.row_height)
        rect.center = self.center.ints()
        return rect


    def coords_to_cell(self, coords: Vector) -> Tuple[int, int]:
        origin = self.get_coords_at(0, 0)
        offset = coords - origin
        x, y = offset.ints()
        return x // self.col_width, y // self.row_height


    def get_player_invulnerability_period(self) -> float:
        # TODO: test if this value is optimal
        # TODO: calculate it dynamically depending on the game state
        return 1.0


    def _can_hit_player(self) -> bool:
        now = time.monotonic()
        return (
            self._last_time_player_hit is None
            or self._last_time_player_hit + self.get_player_invulnerability_period() < now
        )


    def maybe_hit_player(self, damage):
        if not self._can_hit_player():
            return
        now = time.monotonic()
        self._last_time_player_hit = now
        state = get_state()
        state['player_hp'] = max(0, state['player_hp'] - damage)
        logger.debug('Player was hit, {} hp left', state['player_hp'])
        if state['player_hp'] == 0:
            logger.info('Player died')
            # TODO: show game over screen
            sys.exit()


    center = Vector(400, 300)
    rows = 10
    cols = 10
    col_width = 40
    row_height = 40


class FightHpIndicator(FightMixin):
    def __init__(self, fight_script: 'FightScript', rect: pg.Rect):
        super().__init__(fight_script)
        self.rect = rect


    def draw(self, destination: pg.Surface):
        hp_part = self.get_current_hp() / self.get_max_hp()
        filled_width = int(round(self.rect.width * hp_part))
        rect = self.rect
        pg.draw.rect(
            destination,
            (0, 255, 255),
            pg.Rect(rect.left, rect.top, filled_width, rect.height),
        )
        if rect.width > filled_width:
            pg.draw.rect(
                destination,
                (128, 128, 128),
                pg.Rect(rect.left + filled_width, rect.top, rect.width - filled_width, rect.height),
            )

        draw_text(
            f'HP: {self.get_current_hp()}',
            x = rect.right + 10,
            y = rect.top + 4,
            destination = destination,
        )


    def update(self, time_delta: float):
        pass


    def get_current_hp(self):
        return get_state()['player_hp']


    def get_max_hp(self):
        return get_state()['player_max_hp']
