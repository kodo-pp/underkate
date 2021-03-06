from underkate import inventory
from underkate.event_manager import get_event_manager
from underkate.fight.enemy_battle import EnemyBattle
from underkate.fight.mode import Fight
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.items.food import Food
from underkate.items.weapon import Weapon
from underkate.scriptlib.animation import play_animation
from underkate.scriptlib.common import wait_for_event, display_text, sleep
from underkate.scriptlib.fight_enter_animation import FightEnterAnimation
from underkate.scriptlib.money import pay
from underkate.scriptlib.ui import BaseMenu, Menu, BulletBoard, FightHpIndicator, EnemyHpIndicator
from underkate.scriptlib.ui import EnemyNameIndicator
from underkate.sprite import Sprite, BaseSprite
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import BaseTexture
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector
from underkate.wal_list import WalList

import math
import random as rd
from abc import abstractmethod
from pathlib import Path
from types import coroutine
from typing import Optional, Protocol, Dict, Callable, Any, Coroutine, cast, List

import pygame as pg  # type: ignore


async def _play_transition_animation(pos=None):
    animation = FightEnterAnimation(
        narrow_down_length = 0.5,
        remain_length = 0.8,
        pos = get_game().overworld.room.player.pos if pos is None else pos,
        initial_scale = 10.0,
    )
    await play_animation(animation, where=get_game().overworld.room)


async def async_none():
    pass


async def fight(battle, on_after_enter=async_none, on_before_finish=async_none, warning_pos=None):
    game = get_game()
    if warning_pos is None:
        warning_pos = game.overworld.room.player.pos
    await _play_transition_animation(warning_pos)
    await on_after_enter()
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
        return str(self.weapon)


class ConsumeFood(Action):
    def __init__(self, food, inventory_slot):
        self.food = food
        self.inventory_slot = inventory_slot


    def __str__(self):
        return str(self.food)


class Spare(Action):
    def __init__(self, message: str = 'Spare'):
        self.message = message


    def __str__(self):
        return self.message


class Interaction(Action):
    def __init__(self, name: str, pretty_name: str, description: str):
        self.name = name
        self.pretty_name = pretty_name
        self.description = description


    def __str__(self):
        return self.pretty_name


class DoNothing(Action):
    def __str__(self):
        return 'Nothing'


class Submenu(Action):
    def __init__(self, pretty_name: str, submenu: Menu):
        self.pretty_name = pretty_name
        self.submenu = submenu


    def __str__(self):
        return self.pretty_name


class SimpleMenu(Menu):
    def __init__(self, fight_script: 'FightScript', choices: List[Action]):
        super().__init__(fight_script)
        self.choices = choices


    def get_choices(self) -> List[Action]:
        return self.choices


    def get_border_width(self):
        return 0


class HitAnimation:
    class Animator(Sprite):
        def __init__(self, sprite):
            super().__init__(Sprite)
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
            del destination


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
    def __init__(self, pos, texture, clip_rect, bottom, lifetime, momentum, slowdown_factor=1.0):
        safe_clip_rect = clip_rect.clip(texture.get_rect())
        super().__init__(pos, texture.clipped(safe_clip_rect))
        self.bottom = bottom
        self.lifetime = lifetime
        self.momentum = momentum
        self.total_time = 0.0
        self.slowdown_factor = slowdown_factor


    def update(self, time_delta):
        time_delta /= self.slowdown_factor
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
    def __init__(self, texture, pos, slowdown_factor=1.0, where=None):
        self.rect = texture.get_rect()
        self.rect.center = pos.ints()
        self.texture = texture
        self.slowdown_factor = slowdown_factor
        if where is None:
            self.where = get_game().current_game_mode
        else:
            self.where = where


    async def animate(self):
        width, height = self.rect.size
        x_count = (width + self.block_size - 1) // self.block_size
        y_count = (height + self.block_size - 1) // self.block_size
        for x in range(x_count):
            for y in range(y_count):
                particle = self.make_particle(x, y)
                self.where.spawn(particle)

        await sleep(self.max_lifetime * self.slowdown_factor)


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
            slowdown_factor = self.slowdown_factor,
        )
        return particle


    block_size = 5
    max_lifetime = 1.2


class Enemy:
    def __init__(
        self,
        hp: int,
        damage_by_weapon: Dict[str, int],
        #attack: int,
        name: str,
        normal_texture: BaseTexture,
        wounded_texture: BaseTexture,
        pos: Vector,
        fight_script: 'FightScript'
    ):
        self.initial_hp = hp
        self.hp = hp
        self.damage_by_weapon = damage_by_weapon
        #self.attack = attack
        self.name = name
        self.normal_texture = normal_texture
        self.wounded_texture = wounded_texture

        self.fight_script = fight_script
        self.sprite = TexturedSprite(pos, normal_texture)
        fight_script.spawn(self.sprite)


    async def on_kill(self):
        self.sprite.texture = self.wounded_texture


    async def on_disappear(self):
        pos = self.sprite.pos
        self.sprite.kill()
        disappear_animation = DisappearAnimation(self.wounded_texture, pos, where=self.fight_script)
        await disappear_animation.animate()


    async def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            await self.on_kill()


def _load_texture(root, spec):
    filename, _, scale_str = spec.partition('//')
    if _ != '':
        scale = int(scale_str)
        return load_texture(root / filename, scale)
    return load_texture(root / filename)


class Drawable(Protocol):
    def draw(self, destination: pg.Surface):
        ...


class Updatable(Protocol):
    def update(self, time_delta: float):
        ...


class ElementProtocol(Drawable, Updatable, Protocol):
    pass


class FightScript:
    def __init__(self, battle: EnemyBattle):
        # TODO: Rewrite this code since it is absolutely unmaintainable.
        # Some objects start using FightScript before it is fully constructed,
        # which leads to complete nightmare with undefined attributes,
        # which aren't catchable by mypy.
        self.battle = battle
        self.textures = {
            texture_name: _load_texture(battle.root, texture_filename)
            for texture_name, texture_filename in battle.data.get('textures', {}).items()
        }
        self.state: dict = {}

        hp: int = battle.data['hp']
        damage_by_weapon: Dict[str, int] = battle.data.get('damage_by_weapon', {})
        name: str = battle.data['name']

        self.sprites: WalList[BaseSprite] = WalList([])
        self.enemy = Enemy(
            hp = hp,
            damage_by_weapon = damage_by_weapon,
            #attack = attack,
            name = name,
            normal_texture = self.get_enemy_normal_texture(),
            wounded_texture = self.get_enemy_wounded_texture(),
            pos = self.get_enemy_pos(),
            fight_script = self,
        )
        self._has_spared: bool = False
        self.bullet_board: Optional['BulletBoard'] = None
        self._bullet_spawner: Optional['BulletSpawner'] = None
        self.elements: WalList[ElementProtocol] = WalList([
            EnemyNameIndicator(self.enemy, fight_script=self),
            FightHpIndicator(self, pg.Rect(350, 550, 100, 30)),
            EnemyHpIndicator(self.enemy, self, pg.Rect(300, 15, 200, 30)),
        ])


    def get_enemy_normal_texture(self) -> BaseTexture:
        return self.textures['enemy_normal']


    def get_enemy_wounded_texture(self) -> BaseTexture:
        return self.textures['enemy_wounded']


    def get_enemy_pos(self) -> Vector:
        return Vector(400, 200)


    def draw(self, destination: pg.Surface):
        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)
        with self.elements:
            for element in self.elements:
                element.draw(destination)


    def spawn(self, sprite: BaseSprite):
        self.sprites.append(sprite)


    @abstractmethod
    def create_bullet_spawner(self) -> 'BulletSpawner':
        pass


    def update(self, time_delta: float):
        with self.elements:
            for element in self.elements:
                element.update(time_delta)
        if self._bullet_spawner is not None:
            self._bullet_spawner.update(time_delta)
        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)
        self.sprites.filter(lambda x: x.is_alive())


    def get_interactions(self) -> List[Interaction]:
        return []


    def get_choices(self):
        items = list(inventory.enumerate_items(inventory.get_inventory()))
        weapon_choices = [UseWeapon(item) for item in items if isinstance(item, Weapon)]
        food_choices = [
            ConsumeFood(item, i)
            for i, item in enumerate(items) if isinstance(item, Food)
        ]
        return [
            Submenu('Weapons', SimpleMenu(self, weapon_choices)),
            Submenu('Food', SimpleMenu(self, food_choices)),
            Submenu('Interact', SimpleMenu(self, self.get_interactions())),
            Spare(),
        ]


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
            await self.on_spare()
        else:
            txt = DisplayedText([
                TextPage(f'{self.enemy.name} doesn\'t want to\nquit fighting with you', font),
            ])
            await display_text(txt)


    async def on_spare(self):
        get_state()['genocide_route_possible'] = False
        await pay(self.battle.data['reward_for_spare'])


    async def on_hit(self, killed):
        pass


    async def on_kill(self):
        get_state()['pacifist_route_possible'] = False
        await pay(self.battle.data['reward_for_kill'])


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

        await self.on_hit(self.enemy.hp <= 0)

        if self.enemy.hp <= 0:
            txt = DisplayedText([
                TextPage(f'{self.enemy.name} has been killed', font)
            ])
            await self.enemy.on_disappear()
            await sleep(1.0)
            await display_text(txt)
            await self.on_kill()


    async def consume_food(self, food_consumption):
        food = food_consumption.food
        recovered = food.restores
        state = get_state()
        state['player_hp'] += recovered
        if state['player_hp'] >= state['player_max_hp']:
            state['player_hp'] = state['player_max_hp']
            txt = DisplayedText([
                TextPage(f'You ate {food.inline_name} and recovered HP to the maximum'),
            ])
        else:
            txt = DisplayedText([
                TextPage(f'You ate {food.inline_name} and recovered {recovered} HP'),
            ])
        await display_text(txt)
        inventory.remove_from_slot(inventory.get_inventory(), food_consumption.inventory_slot)


    async def interact(self, interaction: Interaction):
        await display_text(
            DisplayedText([
                TextPage(interaction.description),
            ])
        )


    async def get_action_for_choice(self, choice: Action) -> Callable[[], Coroutine[Any, Any, Any]]:
        async def nothing():
            pass

        if choice is None:
            return None
        if isinstance(choice, UseWeapon):
            # Mypy doesn't seem to understand this instance check
            weapon_usage = cast(UseWeapon, choice)
            return lambda: self.use_weapon(weapon_usage.weapon)
        if isinstance(choice, ConsumeFood):
            food_consumption = cast(ConsumeFood, choice)
            return lambda: self.consume_food(food_consumption)
        if isinstance(choice, Spare):
            return self.spare
        if isinstance(choice, DoNothing):
            return nothing
        if isinstance(choice, Interaction):
            interaction = cast(Interaction, choice)
            return lambda: self.interact(interaction)
        assert not isinstance(choice, Submenu)

        raise TypeError(f'Unknown action type: {type(choice)}')


    def can_spare(self):
        return False


    async def perform_attack(self, bullet_board):
        #self.bullet_board = BulletBoard(self)
        self._bullet_spawner = self.create_bullet_spawner()
        await bullet_board.run(duration=5.0)
        self._bullet_spawner = None


    def get_bullet_board(self):
        return BulletBoard(self)


    async def process_enemy_attack(self):
        self.bullet_board = self.get_bullet_board()
        self.elements.append(self.bullet_board)
        await self.perform_attack(self.bullet_board)
        self.elements.filter(lambda x: x is not self.bullet_board)
        self.bullet_board = None


    def has_battle_finished(self):
        return self.enemy.hp <= 0 or self._has_spared


    async def choose_from_menu_tree(self, menu: BaseMenu) -> Action:
        while True:
            result = await self.try_choose_from_menu_tree(menu)
            if result is not None:
                return result


    async def try_choose_from_menu_tree(self, menu: BaseMenu) -> Optional[Action]:
        menu_stack: List[BaseMenu] = [menu]
        while menu_stack:
            choice = await menu_stack[-1].choose()
            if choice is None:
                menu_stack.pop()
            elif isinstance(choice, Submenu):
                menu_stack.append(choice.submenu)
            else:
                return choice
        return None


    async def on_finish(self):
        pass


    def get_battle_entry_text(self):
        return DisplayedText([
            TextPage(f'{self.enemy.name} attacks you'),
        ])


    async def run(self):
        await display_text(self.get_battle_entry_text())
        while True:
            menu = self.get_main_menu()
            choice = await self.choose_from_menu_tree(menu)
            action = await self.get_action_for_choice(choice)
            await action()

            if self.has_battle_finished():
                break
            await self.process_enemy_attack()
            if self.has_battle_finished():
                break
        await self.on_finish()
        get_event_manager().raise_event('fight_finished')


class BaseBullet(Sprite):
    def __init__(
        self,
        *,
        bullet_board: BulletBoard,
        pos: Vector,
        speed: Vector,
        damage: int
    ):
        super().__init__(pos)
        self.bullet_board = bullet_board
        self.speed = speed
        self.damage = damage


    @abstractmethod
    def does_hit_at(self, pos: Vector):
        ...


    def update(self, time_delta: float):
        self.pos += self.speed * time_delta
        if self.does_hit_at(self.bullet_board.get_current_coords()):
            self.bullet_board.maybe_hit_player(self.damage)


class Bullet(BaseBullet):
    def __init__(self, *, texture: BaseTexture, **kwargs):
        super().__init__(**kwargs)
        self.texture = texture


    def draw(self, destination: pg.Surface):
        x, y = self.pos.ints()
        self.texture.draw(destination, x, y)


class RectangularBullet(Bullet):
    @abstractmethod
    def get_hitbox(self) -> pg.Rect:
        ...


    def get_rect(self) -> pg.Rect:
        x, y = self.pos.ints()
        return self.get_hitbox().move(x, y)


    def does_hit_at(self, pos: Vector):
        return bool(self.get_rect().collidepoint(pos.ints()))



class BulletSpawner:
    class TerminateCoroutine(BaseException):
        pass


    def __init__(self, bullet_board):
        self.bullet_board = bullet_board
        self._remaining_sleep_time = 0.0
        self._flow = self._run_wrapper()
        self._flow.send(None)


    async def run(self):
        pass


    async def _run_wrapper(self):
        try:
            await self.run()
        except BulletSpawner.TerminateCoroutine:
            pass
        except StopIteration:
            pass
        get_event_manager().raise_event('attack_finished')


    def spawn(self, bullet, unrestricted: bool = False):
        self.bullet_board.spawn(bullet, unrestricted)


    def set_timeout(self, new_timeout: float):
        self.bullet_board.set_timeout(new_timeout)


    @coroutine
    def sleep_for(self, delay: float):
        self._remaining_sleep_time = delay
        has_timed_out = yield
        if has_timed_out:
            raise BulletSpawner.TerminateCoroutine()


    async def wait_until_timeout(self):
        while True:
            await self.sleep_for(1e+9)


    def update(self, time_delta):
        if self._remaining_sleep_time > 0.0:
            self._remaining_sleep_time -= time_delta
            if self._remaining_sleep_time <= 0.0:
                self._remaining_sleep_time = 0.0
                try:
                    self._flow.send(False)
                except StopIteration:
                    pass


    def on_kill(self):
        try:
            self._flow.send(True)
        except StopIteration:
            pass
