from underkate.event_manager import get_event_manager
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


class Strike(BaseBullet):
    def __init__(
        self,
        location: Vector,
        warning_thickness: int,
        blast_thickness: float,
        blast_displayed_thickness: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.location = location
        self.warning_thickness = warning_thickness
        self.thickness = blast_thickness
        self.displayed_thickness = blast_displayed_thickness
        self._started_at = time.monotonic()


    def get_elapsed_time(self):
        return time.monotonic() - self._started_at


    def is_in_warning_phase(self):
        return self.get_elapsed_time() < self.warning_duration


    def _draw_warning_phase(self, destination):
        t = self.get_elapsed_time() % self.warning_blink_duration
        if t < self.warning_blink_duration / 2:
            color = (255, 0, 0)
        else:
            color = (255, 255, 0)

        pg.draw.line(
            destination,
            color,
            (self.location - Vector(5000, 0)).ints(),
            (self.location + Vector(5000, 0)).ints(),
            self.warning_thickness,
        )
        pg.draw.line(
            destination,
            color,
            (self.location - Vector(0, 5000)).ints(),
            (self.location + Vector(0, 5000)).ints(),
            self.warning_thickness,
        )


    def _draw_strike_phase(self, destination):
        thickness = self._get_current_displayed_thickness()
        pg.draw.line(
            destination,
            (255, 255, 255),
            (self.location - Vector(5000, 0)).ints(),
            (self.location + Vector(5000, 0)).ints(),
            thickness,
        )
        pg.draw.line(
            destination,
            (255, 255, 255),
            (self.location - Vector(0, 5000)).ints(),
            (self.location + Vector(0, 5000)).ints(),
            thickness,
        )


    def draw(self, destination):
        if self.is_in_warning_phase():
            self._draw_warning_phase(destination)
        else:
            self._draw_strike_phase(destination)


    def does_hit_at(self, pos):
        if self.is_in_warning_phase():
            return False
        return any([
            collide_beam_and_point(
                (self.location - Vector(5000, 0), self.location + Vector(5000, 0), self.thickness),
                pos,
            ),
            collide_beam_and_point(
                (self.location - Vector(0, 5000), self.location + Vector(0, 5000), self.thickness),
                pos,
            ),
        ])


    def _get_current_displayed_thickness(self):
        t = self.get_elapsed_time()
        factor = 1.0 + 0.3 * math.sin(t * 25.0)
        bound = clamp(
            (self.warning_duration + self.beam_duration + self.teardown_duration - t)
                / self.teardown_duration,
            0.0,
            1.0,
        )
        return int(round(self.displayed_thickness * factor * bound))


    def is_alive(self):
        return (
            self.get_elapsed_time()
                < self.warning_duration + self.beam_duration + self.teardown_duration
        )


    warning_blink_duration = 0.15
    warning_duration = 0.9
    beam_duration = 0.8
    teardown_duration = 0.1


class AttackSpawner(BulletSpawner):
    async def run(self):
        await rd.choice([self.run_strikes])()


    def _spawn_strike(self, row, col, **kwargs):
        self.spawn(
            Strike(
                bullet_board = self.bullet_board,
                pos = Vector(0, 0),
                speed = Vector(0, 0),
                location = self.bullet_board.get_coords_at(row, col),
                **kwargs,
            ),
        )


    def _spawn_random_strike(self):
        row = rd.randrange(0, 10)
        col = rd.randrange(0, 10)
        self._spawn_strike(
            row = row,
            col = col,
            warning_thickness = 1,
            blast_thickness = 30,
            blast_displayed_thickness = 25,
            damage = 3,
        )


    async def run_strikes(self):
        self.set_timeout(100.0)
        for i in range(4):
            self._spawn_random_strike()
            self._spawn_random_strike()
            self._spawn_random_strike()
            await self.sleep_for(2.2)



class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_rotated = False
        self._has_offered_water = False


    def can_spare(self):
        return self._has_rotated and self._has_offered_water


    def create_bullet_spawner(self):
        return AttackSpawner(bullet_board=self.bullet_board)


    async def _interact_rotate(self):
        if self._has_rotated:
            await display_text(
                DisplayedText([
                    TextPage("Another day has passed, but nothing has really changed"),
                ])
            )
            return

        await display_text(
            DisplayedText([
                TextPage("A lamp in the room simulates the Sun"),
                TextPage("The day smoothly transforms into the evening, which, in turn, turns into the night"),
                TextPage("Then, the morning emerges out of the dark..."),
                TextPage("... as the globe turns its side to the light"),
                TextPage("Globby seems to like this game very much"),
            ])
        )
        self._has_rotated = True
        if self.can_spare():
            await display_text(
                DisplayedText([
                    TextPage("It looks absolutely delighted"),
                ])
            )


    async def _interact_water(self):
        if self._has_offered_water:
            await display_text(
                DisplayedText([
                    TextPage("Remembering how much water it already has, Globby politely refuses"),
                ])
            )
            return

        await display_text(
            DisplayedText([
                TextPage("Globby happily accepts your offering"),
                TextPage("You pour the water right onto it"),
                TextPage("..."),
                TextPage("Globby's ocean levels rise, but not too much"),
                TextPage("Globby admits you've done a fantastic job!"),
            ])
        )
        self._has_offered_water = True
        if self.can_spare():
            await display_text(
                DisplayedText([
                    TextPage("It looks absolutely delighted"),
                ])
            )


    async def _interact_map(self):
        await display_text(
            DisplayedText([
                TextPage("But you have no idea how to draw maps"),
            ])
        )


    async def interact(self, interaction):
        await super().interact(interaction)

        if interaction.name == 'rotate':
            await self._interact_rotate()
        elif interaction.name == 'water':
            await self._interact_water()
        elif interaction.name == 'map':
            await self._interact_map()


    def get_interactions(self):
        return [
            Interaction(
                name = 'map',
                pretty_name = 'Draw a map',
                description = 'A good map might help',
            ),
            Interaction(
                name = 'rotate',
                pretty_name = 'Rotate',
                description = 'You rotate Globby',
            ),
            Interaction(
                name = 'water',
                pretty_name = 'Offer water',
                description = 'You offer Globby some water',
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
