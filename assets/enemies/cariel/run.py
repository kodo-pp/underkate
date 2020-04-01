from underkate import inventory
from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.items.food import Food
from underkate.items.weapon import Weapon
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction, Submenu, SimpleMenu, Action, ConsumeFood
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

import math
import random as rd
from copy import copy
from pathlib import Path

import pygame as pg


class Bit(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-11, -15, 22, 30)


class BouncingBit(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-11, -15, 22, 30)


    def update(self, time_delta):
        super().update(time_delta)
        rect = self.bullet_board.get_rect()
        if self.pos.x < rect.left:
            self.speed.x = abs(self.speed.x)
        if self.pos.x >= rect.right:
            self.speed.x = -abs(self.speed.x)


class EquationBulletSpawner(BulletSpawner):
    async def run(self):
        await rd.choice([self.run_bits, self.run_bouncing_bits])()


    def _spawn_vertical_bit(self):
        row = rd.choice([-1, 10])
        col = rd.randrange(0, 10)
        pos = self.bullet_board.get_coords_at(row, col)
        self.spawn(
            Bit(
                bullet_board = self.bullet_board,
                texture = self.bullet_board.fight_script.textures[f'bit{rd.choice("01")}'],
                pos = pos,
                speed = Vector(0, 200 if row == -1 else -200),
                damage = 3,
            )
        )


    def _spawn_horizontal_bit(self):
        row = rd.randrange(0, 10)
        col = rd.choice([-1, 10])
        pos = self.bullet_board.get_coords_at(row, col)
        self.spawn(
            Bit(
                bullet_board = self.bullet_board,
                texture = self.bullet_board.fight_script.textures[f'bit{rd.choice("01")}'],
                pos = pos,
                speed = Vector(200 if col == -1 else -200, 0),
                damage = 3,
            )
        )


    async def run_bits(self):
        while True:
            await self.sleep_for(0.1)
            rd.choice([self._spawn_vertical_bit, self._spawn_horizontal_bit])()


    async def run_bouncing_bits(self):
        self.set_timeout(10.0)
        pos1 = self.bullet_board.get_coords_at(-1, -1)
        speed1 = Vector(200, 100)
        pos2 = self.bullet_board.get_coords_at(-1, 10)
        speed2 = Vector(-200, 100)
        t = 0.0
        while True:
            await self.sleep_for(0.3)
            t += 0.3
            k = (t * math.sin(t*4) + 1) / 2
            r = 100.0

            offset = Vector(0, -r*k)

            self.spawn(
                BouncingBit(
                    bullet_board = self.bullet_board,
                    texture = self.bullet_board.fight_script.textures[f'bit{rd.choice("01")}'],
                    pos = copy(pos1) + offset,
                    speed = copy(speed1),
                    damage = 1,
                )
            )

            self.spawn(
                BouncingBit(
                    bullet_board = self.bullet_board,
                    texture = self.bullet_board.fight_script.textures[f'bit{rd.choice("01")}'],
                    pos = copy(pos2) + offset,
                    speed = copy(speed2),
                    damage = 1,
                )
            )


class Attack(Action):
    def __str__(self):
        return 'Fight with XXL'


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_spares = 0
        self._num_attacks = 0


    def can_spare(self):
        return self._num_spares > 100


    async def interact(self, interaction):
        await super().interact(interaction)
        if interaction.name == 'close_eyes':
            await display_text(
                DisplayedText([
                    TextPage('You wait a little and then open them up again'),
                    TextPage('Surprisingly, the problem is still here'),
                ])
            )
        elif interaction.name == 'cry':
            await display_text(
                DisplayedText([
                    TextPage('... but the problem absorbs your tears, making your cry worthless'),
                ])
            )


    def get_interactions(self):
        return [
            Interaction(
                name = 'cry',
                pretty_name = 'Cry',
                description = 'You start crying',
            ),
            Interaction(
                name = 'close_eyes',
                pretty_name = 'Close your eyes',
                description = 'You close your eyes, trying to hide from the problem',
            ),
        ]


    def get_choices(self):
        items = list(inventory.enumerate_items(inventory.get_inventory()))
        food_choices = [ConsumeFood(item) for item in items if isinstance(item, Food)]
        return [
            Attack(),
            Submenu('Food', SimpleMenu(self, food_choices)),
            Submenu('Interact', SimpleMenu(self, self.get_interactions())),
            Spare('Refuse to fight'),
        ]


    async def get_action_for_choice(self, choice: Action):
        async def nothing():
            pass

        if choice is None:
            return None
        if isinstance(choice, Attack):
            return self.attack_xxl
        if isinstance(choice, ConsumeFood):
            return lambda: self.consume_food(choice.food)
        if isinstance(choice, Spare):
            return self.spare
        if isinstance(choice, Interaction):
            return lambda: self.interact(choice)
        raise TypeError(f'Unknown action type: {type(choice)}')


    def create_bullet_spawner(self):
        return EquationBulletSpawner(bullet_board=self.bullet_board)


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
