from underkate.event_manager import get_event_manager, Subscriber
from underkate.global_game import get_game
from underkate.overworld.object import Object
from underkate.overworld.pass_map import PassMap
from underkate.overworld.player import Player
from underkate.script import Script, load_script
from underkate.sprite import Sprite
from underkate.texture import BaseTexture
from underkate.vector import Vector
from underkate.wal_list import WalList

from pathlib import Path
from typing import Tuple, List, Mapping, NewType, Callable, Dict, Optional, TYPE_CHECKING

import pygame as pg # type: ignore
import yaml

from loguru import logger


Event = NewType('Event', str)


class Trigger:
    def __init__(self, rect: pg.Rect, event_handlers: Dict[Event, Callable]):
        self.rect = rect
        self.event_handlers = event_handlers


    def handle_event(self, event_name: Event):
        if event_name in self.event_handlers:
            self.event_handlers[event_name]()


    def is_touching(self, rect: pg.Rect) -> bool:
        return bool(self.rect.colliderect(rect))


class TriggerEventWatcher:
    def __init__(self, trigger: Trigger):
        self.trigger = trigger
        self.was_touching = False


    def update(self, player: Player) -> List[Event]:
        events: List[Event] = []
        player_hitbox = player.get_hitbox_with_position()
        is_touching = self.trigger.is_touching(player_hitbox)
        was_touching = self.was_touching
        if is_touching and not was_touching:
            events.append(Event('enter'))
        if not is_touching and was_touching:
            events.append(Event('exit'))

        self.was_touching = is_touching
        return events


    def pass_event(self, event: Event):
        logger.debug('TriggerEventWatcher: pass_event({}, {})', self, event)
        self.trigger.handle_event(event)


class Room:
    def __init__(
        self,
        name: str,
        background: BaseTexture,
        pass_map: PassMap,
        triggers: List[Trigger],
        player_position: Vector,
        scripts: Mapping[str, Callable[[], None]],
        path: Path,
        save_point: Optional[Object],
    ):
        self.name = name
        self.background = background
        self.pass_map = pass_map
        self.trigger_event_watchers = [
            TriggerEventWatcher(trigger)
            for trigger in triggers
        ]
        self.player = Player(player_position)
        self.scripts = scripts
        self.path = path
        self.objects: WalList[Object] = WalList([])
        self.state: dict = {}
        self.sprites: WalList[Sprite] = WalList([])
        self.save_point = save_point
        if save_point is not None:
            self.add_object(save_point)
        get_event_manager().subscribe('key:confirm', Subscriber(self.on_interact))


    def draw(self, surface: pg.Surface):
        x, y = surface.get_rect().center
        self.background.draw(surface, x, y)
        with self.objects:
            for obj in self.objects:
                obj.draw(surface)

        with self.sprites:
            for sprite in self.sprites:
                sprite.draw(surface)

        self.player.draw(surface)


    def is_passable(self, rect: pg.Rect) -> bool:
        return self.pass_map.is_passable(rect) and all(
            obj.can_player_pass(rect)
            for obj in self.objects
        )


    def get_size(self) -> Tuple[int, int]:
        rect = self.pass_map.image.get_rect()
        return rect.width, rect.height


    def update(self, time_delta: float):
        for watcher in self.trigger_event_watchers:
            events = watcher.update(self.player)
            for event in events:
                watcher.pass_event(event)

        self.player.update(time_delta)

        self.objects.filter(lambda x: x.is_alive())
        self.sprites.filter(lambda x: x.is_alive())

        with self.objects:
            for obj in self.objects:
                obj.update()

        with self.sprites:
            for sprite in self.sprites:
                sprite.update(time_delta)


    def on_interact(self, *args):
        if get_game().overworld.room is not self:
            return
        if not get_game().overworld.is_frozen():
            affected_rect = get_game().overworld.room.player.get_extended_hitbox()
            for watcher in self.trigger_event_watchers:
                if affected_rect.colliderect(watcher.trigger.rect):
                    watcher.pass_event(Event('interact'))
        get_event_manager().subscribe('key:confirm', Subscriber(self.on_interact))


    def add_object(self, obj: Object):
        self.objects.append(obj)


    def spawn(self, sprite: Sprite):
        self.sprites.append(sprite)


    def run_script(self, script_name: str):
        self.scripts[script_name]()


    def maybe_run_script(self, script_name: str):
        if script_name in self.scripts:
            self.run_script(script_name)
