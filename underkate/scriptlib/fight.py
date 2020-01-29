from underkate.event_manager import get_event_manager, Subscriber
from underkate.font import load_font
from underkate.text import draw_text
from underkate.texture import load_texture
from underkate.wal_list import WalList
from underkate.scriptlib.common import wait_for_event
from underkate.scriptlib.ui import Menu

from abc import abstractmethod
from typing import Optional

import pygame as pg


async def fight(battle):
    # TODO: rewrite this as this won't work
    event_id, callback = make_callback()
    self.game.enter_fight(battle, callback)
    await wait_for_event(script, event_id)


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


class MainMenu(Menu):
    def get_choices():
        # TODO: player inventory
        return [UseWeapon(Weapon('logic', 'Logic')), Spare(), DoNothing()]


class Enemy:
    def __init__(self, hp, damage_by_weapon, attack):
        self.initial_hp = hp
        self.hp = hp
        self.damage_by_weapon = damage_by_weapon
        self.attack = attack


    def hit(self, damage):
        self.hp -= damage


class FightScript:
    def __init__(self, battle):
        self.battle = battle
        self.textures = {
            texture_name: load_texture(battle.root / texture_filename)
            for texture_name, texture_filename in battle.data.getdefault('textures', {}).items()
        }
        #self.phrases = battle.data['phrases']
        self.sprites = WalList([])
        self.element = None
        self.state = {}

        hp = battle.data['hp']
        damage_by_weapon = battle.data.get('damage_by_weapon', {})
        attack = battle.data['attack']
        self.enemy = Enemy(hp=hp, damage_by_weapon=damage_by_weapon, attack=attack)
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


    def get_main_menu(self):
        return MainMenu(self)


    def get_action_for_choice(self, choice):
        if isinstance(choice, UseWeapon):
            return lambda: self.use_weapon(choice.weapon)
        if isinstance(choice, Spare):
            return self.spare
        if isinstance(choice, DoNothing):
            return lambda: None


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
            self.get_action_for_choice(choice)()
            if self.has_battle_finished():
                break
            await self.process_enemy_attack()
