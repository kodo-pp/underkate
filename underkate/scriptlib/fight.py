from underkate.event_manager import get_event_manager, Subscriber
from underkate.fight.mode import Fight
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import wait_for_event, display_text, make_callback, sleep
from underkate.scriptlib.fight_enter_animation import FightEnterAnimation
from underkate.scriptlib.ui import Menu
from underkate.sprite import Sprite
from underkate.text import DisplayedText, TextPage, draw_text
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector
from underkate.wal_list import WalList

import math
import random as rd
from abc import abstractmethod
from pathlib import Path
from typing import Optional

import pygame as pg  # type: ignore


async def _play_transition_animation():
    event_id, callback = make_callback()
    animation = FightEnterAnimation((800, 600), 0.4, callback)
    get_game().overworld.spawn(animation)
    animation.start_animation()
    await wait_for_event(event_id)


async def fight(battle, on_before_finish):
    game = get_game()
    await _play_transition_animation()
    game.current_game_mode = Fight(battle)
    game.current_game_mode.run()
    await game.current_game_mode.async_show()
    await wait_for_event('fight_finished')
    await game.current_game_mode.async_hide()
    await on_before_finish()
    game.current_game_mode = game.overworld
    await game.current_game_mode.async_show()


class Action:
    @abstractmethod
    def __str__(self):
        pass


class UseWeapon(Action):
    def __init__(self, weapon):
        self.weapon = weapon


    def __str__(self):
        return f'Use weapon: {str(self.weapon)}'


class Weapon:
    def __init__(self, name: str, pretty_name: Optional[str] = None):
        self.name = name
        if pretty_name is None:
            self.pretty_name = self.name
        else:
            self.pretty_name = pretty_name


    def __str__(self):
        return self.pretty_name


class Spare(Action):
    def __str__(self):
        return 'Spare'


class DoNothing(Action):
    def __str__(self):
        return 'Nothing'


class SimpleMenu(Menu):
    def __init__(self, fight_script, choices):
        super().__init__(fight_script)
        self.choices = choices


    def get_choices(self):
        return self.choices


class HitAnimation:
    class Animator(Sprite):
        def __init__(self, sprite):
            self.sprite = sprite
            self.orig_pos = sprite.pos
            self.elapsed_time = 0.0


        async def animate(self):
            get_game().current_game_mode.spawn(self)
            await wait_for_event('hit_animation_finished')
            self.sprite.pos = self.orig_pos


        def calculate_new_pos(self):
            tanh3 = math.tanh(3)
            t = self.elapsed_time / self.length
            k = 0.5 * (tanh3 - math.tanh(6*t - 4)) * math.sin(80*t) / tanh3
            offset = self.half_amplitude * k
            return self.orig_pos + offset


        def draw(self, destination):
            pass


        def update(self, time_delta):
            self.elapsed_time += time_delta
            new_pos = self.calculate_new_pos()
            self.sprite.pos = new_pos


        def is_alive(self):
            return self.elapsed_time < self.length


        def on_kill(self):
            get_event_manager().raise_event('hit_animation_finished')


        length = 0.8
        half_amplitude = Vector(20.0, 3.0)


    def __init__(self, sprite):
        self.animator = HitAnimation.Animator(sprite)


    async def animate(self):
        await self.animator.animate()


class Particle(TexturedSprite):
    def __init__(self, pos, texture, clip_rect, bottom, lifetime, momentum):
        super().__init__(pos, texture.clipped(clip_rect))
        self.bottom = bottom
        self.lifetime = lifetime
        self.momentum = momentum
        self.total_time = 0.0


    def update(self, time_delta):
        self.total_time += time_delta
        if not self.is_alive():
            return
        self.momentum.y += self.gravity * time_delta
        self.pos += self.momentum * time_delta
        self.pos.y = min(self.bottom, self.pos.y)


    def is_alive(self):
        return self.total_time < self.lifetime


    gravity = 1000.0


class DisappearAnimation:
    def __init__(self, texture, pos):
        self.rect = texture.get_rect()
        self.rect.center = pos.ints()
        self.texture = texture


    async def animate(self):
        width, height = self.rect.size
        x_count = (width + self.block_size - 1) // self.block_size
        y_count = (height + self.block_size - 1) // self.block_size
        for x in range(x_count):
            for y in range(y_count):
                particle = self.make_particle(x, y)
                get_game().current_game_mode.spawn(particle)

        await sleep(self.max_lifetime)


    @staticmethod
    def random_between(low, high):
        span = high - low
        return rd.random() * span + low


    def get_pos(self, x, y):
        pos = Vector(*self.rect.topleft) + Vector(x, y) * self.block_size
        return pos


    def get_clip(self, x, y):
        clip_rect = self.rect.copy()
        clip_rect.width = self.block_size
        clip_rect.height = self.block_size
        clip_rect.topleft = (x * self.block_size, y * self.block_size)
        return clip_rect


    def random_momentum(self):
        speed = self.random_between(250.0, 300.0)
        angle_range = math.pi / 12.0
        angle = self.random_between(math.pi / 2.0 - angle_range, math.pi / 2.0 + angle_range)
        direction = Vector(math.cos(angle), -math.sin(angle))
        momentum = direction * speed
        return momentum


    def random_lifetime(self):
        return self.random_between(0.2, self.max_lifetime)


    def random_bottom(self):
        return self.rect.bottom + self.random_between(-10.0, 10.0)


    def make_particle(self, x, y):
        particle = Particle(
            texture = self.texture,
            pos = self.get_pos(x, y),
            clip_rect = self.get_clip(x, y),
            bottom = self.random_bottom(),
            lifetime = self.random_lifetime(),
            momentum = self.random_momentum(),
        )
        return particle


    block_size = 5
    max_lifetime = 1.2


class Enemy:
    def __init__(self, hp, damage_by_weapon, attack, name, normal_texture, wounded_texture, pos):
        self.initial_hp = hp
        self.hp = hp
        self.damage_by_weapon = damage_by_weapon
        self.attack = attack
        self.name = name
        self.normal_texture = normal_texture
        self.wounded_texture = wounded_texture

        self.sprite = TexturedSprite(pos, normal_texture)
        get_game().current_game_mode.spawn(self.sprite)


    async def on_kill(self):
        self.sprite.texture = self.wounded_texture


    async def on_disappear(self):
        pos = self.sprite.pos
        self.sprite.kill()
        disappear_animation = DisappearAnimation(self.wounded_texture, pos)
        await disappear_animation.animate()


    async def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            await self.on_kill()


def _load_texture(root, spec):
    filename, _, scale_str = spec.partition('/')
    if _ != '':
        scale = int(scale_str)
        return load_texture(root / filename, scale)
    return load_texture(root / filename)


class FightScript:
    def __init__(self, battle):
        self.battle = battle
        self.textures = {
            texture_name: _load_texture(battle.root, texture_filename)
            for texture_name, texture_filename in battle.data.get('textures', {}).items()
        }
        #self.phrases = battle.data['phrases']
        self.sprites = WalList([])
        self.element = None
        self.state = {}

        hp = battle.data['hp']
        damage_by_weapon = battle.data.get('damage_by_weapon', {})
        attack = battle.data['attack']
        name = battle.data['name']
        self.enemy = Enemy(
            hp = hp,
            damage_by_weapon = damage_by_weapon,
            attack = attack,
            name = name,
            normal_texture = self.get_enemy_normal_texture(),
            wounded_texture = self.get_enemy_wounded_texture(),
            pos = self.get_enemy_pos(),
        )
        self._has_spared = False


    def get_enemy_normal_texture(self):
        return self.textures['enemy_normal']


    def get_enemy_wounded_texture(self):
        return self.textures['enemy_wounded']


    def get_enemy_pos(self):
        return Vector(400, 200)


    def draw(self, destination):
        if self.element is not None:
            self.element.draw(destination)
        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)


    def spawn(self, sprite):
        self.sprites.append(sprite)


    def update(self, time_delta):
        if self.element is not None:
            self.element.update(time_delta)
        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)


    def get_choices(self):
        return [UseWeapon(Weapon('logic', 'Logic')), Spare(), DoNothing()]


    def get_main_menu(self):
        return SimpleMenu(self, self.get_choices())


    async def spare(self):
        font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        if self.can_spare():
            txt = DisplayedText([
                TextPage(f'You spared {self.enemy.name}', font),
            ])
            await display_text(txt)
            self._has_spared = True
        else:
            txt = DisplayedText([
                TextPage(f'{self.enemy.name} doesn\'t want to\nquit fighting with you', font),
            ])
            await display_text(txt)


    async def use_weapon(self, weapon):
        font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        damage = self.enemy.damage_by_weapon.get(weapon.name, 0)
        await self.enemy.hit(damage)

        await HitAnimation(self.enemy.sprite).animate()

        if damage == 0:
            txt = DisplayedText([
                TextPage("It wasn't effective", font),
            ])
        else:
            txt = DisplayedText([
                TextPage(f'Damage: {damage}', font),
            ])
            await display_text(txt)

        if self.enemy.hp <= 0:
            txt = DisplayedText([
                TextPage(f'{self.enemy.name} has been killed', font)
            ])
            await self.enemy.on_disappear()
            await sleep(1.0)
            await display_text(txt)


    def get_action_for_choice(self, choice):
        async def nothing():
            pass

        if isinstance(choice, UseWeapon):
            return lambda: self.use_weapon(choice.weapon)
        if isinstance(choice, Spare):
            return self.spare
        if isinstance(choice, DoNothing):
            return nothing


    def can_spare(self):
        return False


    async def perform_attack(self):
        await sleep(5)


    async def process_enemy_attack(self):
        bullet_board = self.get_bullet_board()
        self.element = bullet_board
        await self.perform_attack(bullet_board)
        self.element = None


    def has_battle_finished(self):
        return self.enemy.hp <= 0 or self._has_spared


    async def run(self):
        while True:
            menu = self.get_main_menu()
            choice = await menu.choose()
            await self.get_action_for_choice(choice)()
            if self.has_battle_finished():
                break
            await self.process_enemy_attack()
        get_event_manager().raise_event('fight_finished')
