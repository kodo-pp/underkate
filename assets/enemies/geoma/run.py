from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, BaseBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.util import collide_beam_and_point, clamp
from underkate.vector import Vector

import math
import random as rd
import time
from pathlib import Path

import pygame as pg


class Line(BaseBullet):
    def __init__(
        self,
        start: Vector,
        end: Vector,
        thickness: float,
        displayed_thickness: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.start = start
        self.end = end
        self.thickness = thickness
        self.displayed_thickness = displayed_thickness
        self._started_at = time.monotonic()


    def get_elapsed_time(self):
        return time.monotonic() - self._started_at


    def is_in_setup_phase(self):
        return self.get_elapsed_time() < self.setup_duration


    def get_setup_phase_completion_percentage(self):
        return clamp(self.get_elapsed_time() / self.setup_duration, 0.0, 1.0)


    def draw(self, destination):
        if self.is_in_setup_phase():
            k = self.get_setup_phase_completion_percentage()
            brightness = int(clamp(256 * k, 0.0, 256 - 1e-9))
            color = (brightness,) * 3
            pg.draw.circle(destination, color, self.start.ints(), 5)
            pg.draw.circle(destination, color, self.end.ints(), 5)
        else:
            pg.draw.circle(destination, (255, 255, 255), self.start.ints(), 5)
            pg.draw.circle(destination, (255, 255, 255), self.end.ints(), 5)
            thickness = self._get_current_displayed_thickness()
            pg.draw.line(
                destination,
                (255, 255, 255),
                self.start.ints(),
                self.end.ints(),
                thickness,
            )


    def does_hit_at(self, pos):
        if self.is_in_setup_phase():
            return False
        return collide_beam_and_point((self.start, self.end, self.thickness), pos)


    def _get_current_displayed_thickness(self):
        t = self.get_elapsed_time()
        factor = 1.0 + 0.3 * math.sin(t * 25.0)
        bound = clamp(
            (self.setup_duration + self.beam_duration + self.teardown_duration - t)
                / self.teardown_duration,
            0.0,
            1.0,
        )
        return int(round(self.displayed_thickness * factor * bound))


    def is_alive(self):
        return (
            self.get_elapsed_time()
                < self.setup_duration + self.beam_duration + self.teardown_duration
        )


    setup_duration = 0.8
    beam_duration = 1.4
    teardown_duration = 0.2


class LineSpawner(BulletSpawner):
    async def run(self):
        while True:
            await self.sleep_for(0.3)
            if rd.randint(0, 1) == 0:
                row = rd.randrange(0, 10)
                start = self.bullet_board.get_coords_at(row, -1)
                end = self.bullet_board.get_coords_at(row, 10)
            else:
                col = rd.randrange(0, 10)
                start = self.bullet_board.get_coords_at(-1, col)
                end = self.bullet_board.get_coords_at(10, col)
            self.spawn(
                Line(
                    bullet_board = self.bullet_board,
                    pos = Vector(0, 0),
                    speed = Vector(0, 0),
                    damage = 5,
                    start = start,
                    end = end,
                    thickness = 20,
                    displayed_thickness = 8,
                ),
                unrestricted = True,
            )


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__is_player_scared = False


    def can_spare(self):
        return self.__is_player_scared


    async def on_kill(self):
        get_state()['pacifist_route_possible'] = False


    async def on_spare(self):
        get_state()['genocide_route_possible'] = False


    def create_bullet_spawner(self):
        return LineSpawner(bullet_board=self.bullet_board)


async def run(*, enemy_battle, **kwargs):
    global fs
    fs = Script(enemy_battle)
    await fs.run()


async def draw(*, destination, **kwargs):
    global fs
    fs.draw(destination)


async def update(*, time_delta, **kwargs):
    global fs
    fs.update(time_delta)
