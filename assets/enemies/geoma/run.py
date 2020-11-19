from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, BaseBullet, RectangularBullet
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


    setup_duration = 1.0
    beam_duration = 1.2
    teardown_duration = 0.2


class Triangle(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-40, -35, 80, 70)


class Spawner(BulletSpawner):
    async def run(self):
        await rd.choice([self.run_triangles, self.run_chaotic_lines])()


    async def run_line_grid(self):
        self.set_timeout(100.0)

        for i in range(0, 10, 3):
            self._spawn_line(i, -1, i, 10)
            self._spawn_line(-1, i, 10, i)

        await self.sleep_for(2.8)

        for i in range(1, 10, 3):
            self._spawn_line(i, -1, i, 10)
            self._spawn_line(-1, i, 10, i)

        await self.sleep_for(2.8)


    async def run_triangles(self):
        self.set_timeout(100.0)
        for i in range(9):
            self._spawn_triangle()
            await self.sleep_for(0.6)


    def _spawn_triangle(self):
        pi3 = math.pi / 3
        angle = rd.choice([0, pi3, 2 * pi3, 3 * pi3, 4 * pi3, 5 * pi3])
        direction = Vector(math.cos(angle), math.sin(angle))
        angle_margin = 1.0
        spawn_angle = rd.uniform(angle - angle_margin, angle + angle_margin)
        spawn_radius = 300
        coords = Vector(*self.bullet_board.get_rect().center)
        spawn_pos = coords - Vector(math.cos(spawn_angle), math.sin(spawn_angle)) * spawn_radius
        velocity = 200
        self.spawn(
            Triangle(
                bullet_board = self.bullet_board,
                pos = spawn_pos,
                speed = direction * velocity,
                damage = 3,
                texture = self.bullet_board.fight_script.textures['triangle'],
            )
        )

    def _spawn_line(self, r1, c1, r2, c2):
        start = self.bullet_board.get_coords_at(r1, c1)
        end = self.bullet_board.get_coords_at(r2, c2)
        self.spawn(
            Line(
                bullet_board = self.bullet_board,
                pos = Vector(0, 0),
                speed = Vector(0, 0),
                damage = 4,
                start = start,
                end = end,
                thickness = 20,
                displayed_thickness = 8,
            ),
            unrestricted = True,
        )


    async def run_chaotic_lines(self):
        while True:
            await self.sleep_for(0.4)
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
        self._can_spare = False


    def can_spare(self):
        return self._can_spare


    def create_bullet_spawner(self):
        return Spawner(bullet_board=self.bullet_board)


    async def interact(self, interaction):
        await super().interact(interaction)

        if interaction.name == 'cry':
            await display_text(
                DisplayedText([
                    TextPage("... but Geoma doesn't care"),
                ])
            )
        elif interaction.name == 'circle':
            await display_text(
                DisplayedText([
                    TextPage("Geoma recognizes an old friend in your drawing"),
                    TextPage("She looks much happier now"),
                ])
            )
            self._can_spare = True


    def get_interactions(self):
        return [
            Interaction(
                name = 'cry',
                pretty_name = 'Start crying',
                description = 'You start crying. Tears are running down your cheeks',
            ),
            Interaction(
                name = 'circle',
                pretty_name = 'Draw a circle',
                description = 'You find some paper and draw a circle on it',
            ),
        ]


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
