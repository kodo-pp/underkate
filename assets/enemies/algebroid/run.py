from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector

import random as rd
from pathlib import Path

import pygame as pg


class EquationBullet(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-3, -10, 13, 20)


class EquationBulletSpawner(BulletSpawner):
    async def run(self):
        while True:
            await self.sleep_for(0.2)
            row = -1
            col = rd.randrange(0, 10)
            pos = self.bullet_board.get_coords_at(row, col)
            self.spawn(
                EquationBullet(
                    bullet_board = self.bullet_board,
                    texture = self.bullet_board.fight_script.textures['equation_bullet'],
                    pos = pos,
                    speed = Vector(0, 150),
                    damage = 3,
                )
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


    async def interact(self, interaction):
        await super().interact(interaction)
        if interaction.name == 'get_scared':
            self.__is_player_scared = True

        await display_text(
            DisplayedText([
                TextPage('Algebroid feels that you are not dangerous and is likely to let you go now'),
            ])
        )


    def get_interactions(self):
        return [
            Interaction(
                name = 'get_scared',
                pretty_name = 'Get scared',
                description = 'You get scared by the problem and look very frightened',
            ),
        ]


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
