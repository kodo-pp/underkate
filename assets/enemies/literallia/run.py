from underkate.animated_texture import AnimatedTexture
from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.inventory import get_inventory, give
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.util import collide_beam_and_point, clamp
from underkate.vector import Vector
from underkate.walking_npc import WalkingNpc

import math
import random as rd
import time
from pathlib import Path

import pygame as pg


class LetterBullet(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-10, -10, 20, 20)


class Book(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-65, -85, 130, 170)


    def update(self, time_delta):
        super().update(time_delta)
        rect = self.bullet_board.get_rect()
        if self.pos.x < rect.left:
            self.speed.x = abs(self.speed.x)
        if self.pos.x >= rect.right:
            self.speed.x = -abs(self.speed.x)
        if self.pos.y < rect.top:
            self.speed.y = abs(self.speed.y)
        if self.pos.y >= rect.bottom:
            self.speed.y = -abs(self.speed.y)


class LiteralliaBulletSpawner(BulletSpawner):
    async def run(self):
        await rd.choice([self.run_book, self.run_letters])()


    async def run_letters(self):
        while True:
            await self.sleep_for(0.2)
            row = rd.randrange(0, 10)
            pos = self.bullet_board.get_coords_at(row, 10)

            self.spawn(
                LetterBullet(
                    bullet_board = self.bullet_board,
                    pos = pos,
                    speed = Vector(-180, rd.randint(0, 150) - 15 * row),
                    damage = 4,
                    texture = self.bullet_board.fight_script.textures['letter_bullet'],
                ),
            )


    async def run_book(self):
        self.spawn(
            Book(
                bullet_board = self.bullet_board,
                pos = self.bullet_board.get_coords_at(-1, 8),
                speed = Vector(rd.randint(160, 220), rd.randint(160, 220)) * 1.3,
                damage = 6,
                texture = self.bullet_board.fight_script.textures['book_bullet'],
            ),
        )
        await self.wait_until_timeout()


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_attacks = 0
        self._can_spare = False


    def can_spare(self):
        return self._can_spare


    async def process_enemy_attack(self):
        await super().process_enemy_attack()
        self._num_attacks += 1
        if self._num_attacks == 3:
            flate_texture = AnimatedTexture(
                [
                    load_texture(Path('.') / 'assets' / 'textures' / 'flate' / 'fight.png', scale=4),
                ],
                fps = 1,
            )
            flate = WalkingNpc(
                pos = Vector(-100, 100),
                left = flate_texture,
                right = flate_texture,
                front = flate_texture,
                back = flate_texture,
                speed = 200.0,
            )
            self.spawn(flate)
            await flate.walk_x(300.0)
            await display_text(load_text('fight/lyceum/literallia/flate_intervention'))
            await flate.walk_x(-300.0)
            flate.kill()
            give(get_inventory(), 'nonsense')


    async def use_weapon(self, weapon):
        await super().use_weapon(weapon)
        if weapon.name == 'nonsense' and not self._can_spare:
            await display_text(load_text('fight/lyceum/literallia/phd'))
            self._can_spare = True


    async def on_kill(self):
        get_state()['pacifist_route_possible'] = False


    async def on_spare(self):
        get_state()['genocide_route_possible'] = False


    def create_bullet_spawner(self):
        return LiteralliaBulletSpawner(bullet_board=self.bullet_board)


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
