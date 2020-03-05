from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet, BulletSpawner
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

import random as rd
from pathlib import Path

import pygame as pg


class EquationBullet(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-10, -10, 20, 20)


class EquationBulletSpawner(BulletSpawner):
    async def run(self):
        while True:
            await self.sleep_for(0.2)
            self.spawn(
                EquationBullet(
                    bullet_board = self.bullet_board,
                    texture = self.bullet_board.fight_script.textures['equation_bullet'],
                    row = -1,
                    col = rd.randrange(0, 10),
                    speed = Vector(0, 150),
                    damage = 3,
                )
            )


class Script(FightScript):
    def can_spare(self):
        return True


    def get_choices(self):
        return [UseWeapon(Weapon('Test weapon', 'Test weapon')), Spare()]


    async def on_kill(self):
        get_state()['pacifist_route_possible'] = False


    async def on_spare(self):
        get_state()['genocide_route_possible'] = False


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
