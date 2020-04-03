from underkate import inventory
from underkate.animated_sprite import AnimatedSprite
from underkate.animated_texture import AnimatedTexture
from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.items.food import Food
from underkate.items.weapon import Weapon
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.scriptlib.fight import BulletSpawner, Interaction, Submenu, SimpleMenu, Action, ConsumeFood
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, RectangularBullet, EnemyHpIndicator
from underkate.scriptlib.fight import HitAnimation, DisappearAnimation
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.textured_walking_sprite import TexturedWalkingSprite
from underkate.util import clamp
from underkate.vector import Vector

import math
import random as rd
from copy import copy
from pathlib import Path

import pygame as pg


class Attack(Action):
    def __str__(self):
        return 'Use XXL'


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_spares = 0
        self._num_attacks = 0
        self.elements.filter(lambda x: not isinstance(x, EnemyHpIndicator))
        self._spawn_cariel_sprite()
        self._resolution = None


    def _spawn_cariel_sprite(self):
        texture = AnimatedTexture([self.textures['cariel']], fps=1)
        self.cariel_sprite = TexturedWalkingSprite(
            pos = Vector(200, 200),
            left = texture,
            right = texture,
            front = texture,
            back = texture,
            speed = 200,
        )
        self.spawn(self.cariel_sprite)


    def get_choices(self):
        return [
            Attack(),
            Spare(),
        ]


    async def get_action_for_choice(self, choice: Action):
        async def nothing():
            pass

        if choice is None:
            return None
        if isinstance(choice, Attack):
            return self.attack_xxl
        if isinstance(choice, Spare):
            return self.spare
        raise TypeError(f'Unknown action type: {type(choice)}')


    def create_bullet_spawner(self):
        raise NotImplementedError()


    def get_battle_entry_text(self):
        return DisplayedText([
            TextPage('Cariel is attacked by you'),
            TextPage('He looks terrified'),
        ])


    def get_kill_text(self):
        return DisplayedText([
            TextPage(
                '...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.07,
            ),
            TextPage(
                'all...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.07,
            ),
            TextPage(
                'my tasks...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.07,
            ),
            TextPage(
                '... are solved?',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.07,
            ),
            TextPage(
                '...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.07,
            ),
            TextPage(
                'That is what I was afraid of',
                picture = self.textures['cariel_desperate'],
                delay = 0.07,
            ),
            TextPage(
                'The only thing you do',
                picture = self.textures['cariel_desperate'],
                delay = 0.07,
            ),
            TextPage(
                '... is solving tasks and meeting deadlines',
                picture = self.textures['cariel_desperate'],
                delay = 0.07,
            ),
            TextPage(
                'And, as a result, destroying our minds and powers...',
                picture = self.textures['cariel_desperate'],
                delay = 0.07,
            ),
            TextPage(
                'DESTROYING OUR SOULS...',
                picture = self.textures['cariel_shouting'],
                delay = 0.3,
                skippable = False,
            ),
            TextPage(
                'It turned out that XXL was not meant as a means of self-defense for you...',
                picture = self.textures['cariel_desperate'],
                delay = 0.09,
            ),
            TextPage(
                'But instead, it was protecting us, teachers, from your destructive passions',
                picture = self.textures['cariel_desperate'],
                delay = 0.09,
            ),
            TextPage(
                'BUT YOU DESTROYED THIS PROTECTIVE BARRIER',
                picture = self.textures['cariel_shouting'],
                delay = 0.3,
                skippable = False,
            ),
            TextPage(
                '...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.15,
            ),
            TextPage(
                'Please...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.15,
            ),
            TextPage(
                'Do not be like that...',
                picture = self.textures['cariel_desperate'],
                delay = 0.2,
            ),
            TextPage(
                'I know you can be good...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.25,
            ),
            TextPage(
                'My child...',
                picture = self.textures['cariel_closed_eyes'],
                delay = 0.4,
            ),
        ])


    def get_spare_text(self):
        return DisplayedText([
            TextPage(
                '...',
                picture = self.textures['cariel_frightened'],
            ),
            TextPage(
                '...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'Oh...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'Despite being about to end all my problems and to take away my soul...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                '... you decided to leave everything as it is',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'I... I cannot find suitable words to express how I feel about that',
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                'I feel... relief, joy...',
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                '... care',
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                '...',
                picture = self.textures['cariel_thinking'],
            ),
            TextPage(
                'To be honest, I thought initially that XXL may be a good way of self-defense against problems',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'But now I am sure it can be misused too easily',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                "And I am extremely happy that you did not fall into this trap of destroying teachers' souls...",
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                "... just because you wanted to show your proficience in solving various tasks",
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                'You have expanded my mind very much, dear student',
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                'So I will definitely stop blocking your way',
                picture = self.textures['cariel_smiling'],
            ),
            TextPage(
                'But...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'If you choose to return here...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'Please, do not try to find me',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'I would have a lot of work to do and...',
                picture = self.textures['cariel_desperate'],
            ),
            TextPage(
                '... I would have to reconsider the values in my life',
                picture = self.textures['cariel_desperate'],
            ),
            TextPage(
                'Such as the value of teaching a student how to use XXL...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                '...',
                picture = self.textures['cariel_thinking'],
            ),
            TextPage(
                'So...',
                picture = self.textures['cariel_neutral'],
            ),
            TextPage(
                'Goodbye, student!',
                picture = self.textures['cariel_smiling'],
            ),
        ])


    async def spare(self):
        self._resolution = 'spare'
        await display_text(self.get_spare_text())
        get_state()['cariel_fought'] = True
        await self.cariel_sprite.walk_x(-300)
        await self.on_spare()


    async def attack_xxl(self):
        await self.enemy.hit(0)

        await HitAnimation(self.enemy.sprite).animate()

        await display_text(DisplayedText([TextPage('You start XXL and solve all the problems you can find')]))

        self._resolution = 'kill'

        inflash = Flash(size=(800, 600), length=1.0).start_animation()
        self.spawn(inflash)
        await sleep(1.5)
        inflash.kill()

        self.enemy.sprite.texture = self.enemy.wounded_texture

        outflash = Flash(size=(800, 600), length=0.3, is_reversed=True).start_animation()
        self.spawn(outflash)
        await sleep(0.31)
        outflash.kill()

        await sleep(1.0)
        await self.enemy.on_disappear()
        await sleep(1.0)

        await display_text(self.get_kill_text())

        disappear_animation = DisappearAnimation(
            pos = self.cariel_sprite.pos,
            texture = self.textures['cariel'],
            slowdown_factor = 4,
        )
        self.cariel_sprite.kill()
        await disappear_animation.animate()
        await sleep(1)

        txt = DisplayedText([
            TextPage('Cariel has been killed'),
        ])
        await display_text(txt)
        await self.on_kill()
        get_state()['cariel_fought'] = True


    def has_battle_finished(self):
        return self._resolution is not None


class Flash(AnimatedSprite):
    def __init__(self, size, length=0.5, is_reversed=False):
        super().__init__()
        self.length = length
        self.is_reversed = is_reversed
        self.surface = pg.Surface(size)
        self.surface = self.surface.convert_alpha()
        self._killed = False


    def update(self, time_delta: float):
        pass


    def kill(self):
        super().kill()
        self._killed = True


    def has_animation_finished(self):
        return self._killed


    def calculate_alpha_coefficient(self, elapsed_time: float) -> float:
        return clamp(
            (self.length - elapsed_time if self.is_reversed else elapsed_time) / self.length,
            0.0,
            1.0,
        )


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
