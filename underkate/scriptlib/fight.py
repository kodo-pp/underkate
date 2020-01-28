from underkate.event_manager import get_event_manager, Subscriber
from underkate.font import load_font
from underkate.text import draw_text
from underkate.texture import load_texture
from underkate.wal_list import WalList
from underkate.scriptlib.common import wait_for_event

from abc import abstractmethod
from typing import Optional


async def fight(battle):
    # TODO: rewrite this as this won't work
    event_id, callback = make_callback()
    self.game.enter_fight(battle, callback)
    await wait_for_event(script, event_id)


class Menu:
    def __init__(self, fight_script):
        self.fight_script = fight_script


    async def choose(self):
        self.index = 0
        self.font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        self.choices = self.get_choices()
        self.pointer_texture = load_texture(Path('.') / 'assets' / 'fight' / 'pointer.png', scale=2)
        self.fight_script.element = self
        while True:
            event, key = await


    def draw(self, destination):
        for i, choice in enumerate(self.choices):
            draw_text(str(choice), font = self.font, x = 200, y = 300 + 40 * i, destination = destination)
        self.pointer_texture.draw(destination, x = 160, y = 300 + 40 * self.index)


    def update(self, time_delta):
        pass


    def on_key_up(self):
        if not self.is_alive():
            return
        self.index = max(self.index - 1, 0)
        get_event_manager().subscribe('key:up', Subscriber(lambda *args: self.on_key_up()))


    def on_key_down(self):
        if not self.is_alive():
            return
        self.index = min(self.index + 1, len(self.choices) - 1)
        get_event_manager().subscribe('key:down', Subscriber(lambda *args: self.on_key_down()))


    def is_alive(self):
        return fight_script.current_game_mode is self


    @abstractmethod
    def get_choices(self):
        ...


    def on_choice_made(self, choice):
        get_event_manager().raise_event('choice_made', choice)


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


class FightScript:
    def __init__(self, battle):
        self.battle = battle
        self.textures = {
            texture_filename: load_texture(battle.root / '')
            for texture_filename in battle.data.getdefault('textures', [])
        }
        self.phrases = battle.data['phrases']
        self.sprites = WalList([])
        self.current_screen = MainMenu(self)
        self.state = {}


    def draw(self, destination):
        self.current_screen.draw(destination)
        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(destination)


    def spawn(self, sprite):
        self.sprites.append(sprite)


    def update(self, time_delta):
        self.current_screen.update(time_delta)
        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)
