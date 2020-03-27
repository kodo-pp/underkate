from underkate.animated_sprite import AnimatedSprite
from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.scriptlib.fight import BulletSpawner, Interaction
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.util import clamp
from underkate.vector import Vector

import random as rd
from pathlib import Path

import pygame as pg


class Tear(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-10, -10, 20, 20)


class TearSpawner(BulletSpawner):
    async def run(self):
        while True:
            await self.sleep_for(0.15)
            col = rd.randrange(0, 10)
            pos = self.bullet_board.get_coords_at(-1, col)
            player_pos = self.bullet_board.get_current_coords()
            direction = (player_pos - pos).normalized()
            speed = direction * 180

            self.spawn(
                Tear(
                    bullet_board = self.bullet_board,
                    texture = self.bullet_board.fight_script.textures['tear'],
                    pos = pos,
                    speed = speed,
                    damage = 3,
                )
            )


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_attacks = 0
        self._exploded = False


    def can_spare(self):
        return False


    async def process_enemy_attack(self):
        pic = self.textures['unknown']
        if self._num_attacks == 0:
            txt = DisplayedText([
                TextPage('Oh no! It has got out of control!', picture=pic),
                TextPage('This beast will destroy everything with its tears!', picture=pic),
            ])
            await display_text(txt)
        elif self._num_attacks == 1:
            txt = DisplayedText([
                TextPage("There's no way to stop this flood of tears", picture=pic),
                TextPage('Nothing we can do to save this place', picture=pic),
            ])
            await display_text(txt)
        elif self._num_attacks == 2:
            txt = DisplayedText([
                TextPage('Wait...', picture=pic),
                TextPage('It looks like a might know a way to stop this cry', picture=pic),
                TextPage('Just give me a sec...', picture=pic),
            ])
            await display_text(txt)
        elif self._num_attacks == 3:
            txt = DisplayedText([
                TextPage("I'll try now to neutralize the Crier", picture=pic),
                TextPage('Sooooo.... we just have to.... NONONONONONONO', picture=pic),
                TextPage("I MADE A SINGLE WRONG MOVE", picture=pic),
                TextPage("AND NOW IT'S EXPLODING!......", picture=pic, skippable=False),
            ])
            await display_text(txt)
            self._exploded = True
            return

        await super().process_enemy_attack()
        self._num_attacks += 1


    def has_battle_finished(self):
        return self._exploded


    def create_bullet_spawner(self):
        return TearSpawner(bullet_board=self.bullet_board)


    async def on_finish(self):
        explosion = Explosion(size=(800, 600)).start_animation()
        fs.spawn(explosion)
        explosion.start_animation()
        await sleep(0.7)


class Explosion(AnimatedSprite):
    def __init__(self, size, length = 0.5):
        super().__init__()
        self.length = length
        self.surface = pg.Surface(size)
        self.surface = self.surface.convert_alpha()


    def update(self, time_delta: float):
        pass


    def has_animation_finished(self):
        return False


    def calculate_alpha_coefficient(self, elapsed_time: float) -> float:
        return clamp(elapsed_time / self.length, 0.0, 1.0)


    def draw_frame(self, surface: pg.Surface, elapsed_time: float):
        alpha_coefficient = self.calculate_alpha_coefficient(elapsed_time)
        alpha = int(round(alpha_coefficient * 255))
        self.surface.fill((255, 255, 255, alpha))
        surface.blit(self.surface, surface.get_rect())


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
