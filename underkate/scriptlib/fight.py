from underkate.event_manager import get_event_manager, Subscriber
from underkate.fight.mode import Fight
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.scriptlib.common import wait_for_event, display_text, make_callback
from underkate.scriptlib.fight_enter_animation import FightEnterAnimation
from underkate.scriptlib.ui import Menu
from underkate.text import DisplayedText, TextPage, draw_text
from underkate.texture import load_texture
from underkate.wal_list import WalList

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


class Enemy:
    def __init__(self, hp, damage_by_weapon, attack, name):
        self.initial_hp = hp
        self.hp = hp
        self.damage_by_weapon = damage_by_weapon
        self.attack = attack
        self.name = name


    def hit(self, damage):
        self.hp -= damage


class FightScript:
    def __init__(self, battle):
        self.battle = battle
        self.textures = {
            texture_name: load_texture(battle.root / texture_filename)
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
        self.enemy = Enemy(hp=hp, damage_by_weapon=damage_by_weapon, attack=attack, name=name)
        self._has_spared = True


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
        self.enemy.hit(damage)

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
                TextPage('The enemy has been killed', font)
            ])
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
