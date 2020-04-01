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
        self.elements.filter(lambda x: not isinstance(x, EnemyHpIndicator))
        self._spawn_cariel_sprite()


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


    def get_text_for_current_spare(self):
        if self._num_spares == 1:
            return DisplayedText([
                TextPage(
                    'Yes, exactly, you are not expected to fight with anyone',
                    picture = self.textures['cariel_smiling'],
                ),
                TextPage(
                    'Instead, let us open XXL',
                    picture = self.textures['cariel_smiling'],
                ),
            ])
        if self._num_spares == 2:
            return DisplayedText([
                TextPage(
                    'Yes, exactly, now copy these cells...',
                    picture = self.textures['cariel_smiling'],
                ),
            ])
        if self._num_spares == 3:
            return DisplayedText([
                TextPage(
                    '...',
                    picture = self.textures['cariel_neutral'],
                ),
            ])
        if self._num_spares == 4:
            return DisplayedText([
                TextPage(
                    'Wait, what are you trying to do?',
                    picture = self.textures['cariel_neutral'],
                ),
            ])
        if self._num_spares == 5:
            return DisplayedText([
                TextPage(
                    'What are you trying to achieve by this?',
                    picture = self.textures['cariel_dissat_c'],
                ),
            ])
        if self._num_spares == 6:
            return DisplayedText([
                TextPage(
                    'Please...',
                    picture = self.textures['cariel_dissat_r'],
                ),
                TextPage(
                    'Just open XXL',
                    picture = self.textures['cariel_begging'],
                ),
            ])
        if self._num_spares == 7:
            return DisplayedText([
                TextPage(
                    'I know it is not perfect, but...',
                    picture = self.textures['cariel_begging'],
                ),
                TextPage(
                    '... but please, just use it for me',
                    picture = self.textures['cariel_begging'],
                ),
            ])
        if self._num_spares == 8:
            return DisplayedText([
                TextPage(
                    '...',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    'Well, I understand',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    'Some people may not like certain tools or methods',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    'And this is why it was not right for me to force you to learn XXL',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    '...',
                    picture = self.textures['cariel_thinking'],
                ),
                TextPage(
                    'Dear student',
                    picture = self.textures['cariel_smiling'],
                ),
                TextPage(
                    'For your sake I will put my habits and favors aside',
                    picture = self.textures['cariel_smiling'],
                ),
                TextPage(
                    'XXL may indeed be too easy to misuse',
                    picture = self.textures['cariel_smiling'],
                ),
                TextPage(
                    'You may accidentally solve some problems, by which you will hurt someone or even...',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    '...',
                    picture = self.textures['cariel_desperate'],
                ),
                TextPage(
                    'Well, let us not think about it',
                    picture = self.textures['cariel_smiling'],
                ),
                TextPage(
                    'The thing is that... you should probably choose your tools yourself',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    'I should have respected your freedom from the very beginning',
                    picture = self.textures['cariel_neutral'],
                ),
                TextPage(
                    'So... I will cease blocking your path further now',
                    picture = self.textures['cariel_neutral'],
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
                    'Goodbye, my child! :)',
                    picture = self.textures['cariel_smiling'],
                ),
            ])


    def get_text_for_current_attack(self):
        if self._num_attacks == 1:
            return DisplayedText([
                TextPage('You beat up the keyboard'),
                TextPage('You have just typed complete nonsense'),
                TextPage('Yes, go on like that', picture=self.textures['cariel_smiling']),
            ])
        if self._num_attacks == 2:
            return DisplayedText([
                TextPage('You beat the keyboard harder'),
                TextPage('Wow, you\'ve calculated 5 - 3 = 2'),
                TextPage('Going in the right direction', picture=self.textures['cariel_smiling']),
            ])
        if self._num_attacks == 3:
            return DisplayedText([
                TextPage('You smash the keyboard at the full force'),
                TextPage('Surprisingly, something meaningful shows up on the screen'),
                TextPage('Wow, making progress!', picture=self.textures['cariel_smiling']),
            ])
        if self._num_attacks == 4:
            return DisplayedText([
                TextPage('You throw the mouse away'),
                TextPage('However, it manages to copy the cells exactly the way you need'),
                TextPage('Halfway through!', picture=self.textures['cariel_smiling']),
            ])
        if self._num_attacks == 5:
            return DisplayedText([
                TextPage('You shout at the screen'),
                TextPage('Voice recognition almost completes the formula'),
                TextPage('Almost done!', picture=self.textures['cariel_smiling']),
            ])
        if self._num_attacks == 6:
            return DisplayedText([
                TextPage('You create a macro written in VBA'),
                TextPage('Suddenly, something strange starts happening...'),
                TextPage('Wait, what is going on?', picture=self.textures['cariel_neutral']),
                TextPage(
                    'STOP, IT IS NOT SUPPOSED TO WORK THIS WAY, NOOOOOOO...',
                    picture = self.textures['cariel_frightened'],
                ),
            ])


    def has_killed_xxl(self):
        return self._num_attacks >= 6


    async def spare(self):
        if self._num_attacks > 0:
            await display_text(DisplayedText([TextPage('...?', picture=self.textures['cariel_neutral'])]))
            return

        self._num_spares += 1
        await display_text(self.get_text_for_current_spare())
        self._has_spared = self.check_if_has_spared()
        if self._has_spared:
            get_state()['cariel_fought'] = True
            await self.cariel_sprite.walk_x(-300)
            await self.on_spare()


    def check_if_has_spared(self):
        return self._num_spares >= 8


    async def attack_xxl(self):
        await self.enemy.hit(0)

        await HitAnimation(self.enemy.sprite).animate()

        self._num_attacks += 1
        await display_text(self.get_text_for_current_attack())
        if self.has_killed_xxl():
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

            await display_text(
                DisplayedText([
                    TextPage(
                        '...',
                        picture = self.textures['cariel_surprised'],
                    ),
                    TextPage(
                        'My problems...',
                        picture = self.textures['cariel_surprised'],
                    ),
                    TextPage(
                        'They are all... solved?',
                        picture = self.textures['cariel_surprised'],
                    ),
                    TextPage(
                        'You managed to do everything so easily?',
                        picture = self.textures['cariel_surprised'],
                    ),
                    TextPage(
                        'Oh my, oh no...',
                        picture = self.textures['cariel_desperate'],
                    ),
                    TextPage(
                        'This went further than it was supposed to...',
                        picture = self.textures['cariel_desperate'],
                    ),
                    TextPage(
                        'I lost my problems... I lost my powers...',
                        picture = self.textures['cariel_desperate'],
                    ),
                    TextPage(
                        'I lost the energy that kept me alive...',
                        picture = self.textures['cariel_closed_eyes'],
                    ),
                    TextPage(
                        '...',
                        picture = self.textures['cariel_closed_eyes'],
                    ),
                    TextPage(
                        'But...',
                        picture = self.textures['cariel_desperate'],
                    ),
                    TextPage(
                        'I still believe in you',
                        picture = self.textures['cariel_desperate'],
                    ),
                    TextPage(
                        'You are strong enough to survive, you have just proved it...',
                        picture = self.textures['cariel_closed_eyes'],
                        delay = 0.15,
                    ),
                    TextPage(
                        'My child.....',
                        picture = self.textures['cariel_closed_eyes'],
                        delay = 0.3,
                    ),
                ]),
            )

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
        return self._has_spared or self.has_killed_xxl()


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
