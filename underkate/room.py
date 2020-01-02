from .pass_map import PassMap
from .player import Player
from .texture import BaseTexture, load_texture

from pathlib import Path
from typing import Union, cast, Tuple, List, Dict, NewType, Callable

import pygame as pg
import yaml


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
        events = []

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
        self.trigger.handle_event(event)


class Room:
    def __init__(
        self,
        background: BaseTexture,
        pass_map: PassMap,
        triggers: List[Trigger],
    ):
        self.background = background
        self.pass_map = pass_map
        self.trigger_event_watchers = [
            TriggerEventWatcher(trigger)
            for trigger in triggers
        ]

    def draw(self, surface: pg.Surface):
        x, y = surface.get_rect().center
        self.background.draw(surface, x, y)

    def is_passable(self, rect: pg.Rect) -> bool:
        return self.pass_map.is_passable(rect)

    def get_size(self) -> Tuple[int, int]:
        rect = self.pass_map.image.get_rect()
        return rect.width, rect.height

    def update(self, player: Player):
        for watcher in self.trigger_event_watchers:
            events = watcher.update(player)
            for event in events:
                watcher.pass_event(event)


def load_room(path: Union[Path, str]) -> Room:
    if isinstance(path, str):
        path = Path(path)

    with open(path / 'room.yml') as f:
        data = yaml.safe_load(f)

    background_filename = path / cast(str, data['background'])
    pass_map_filename = path / cast(str, data['pass_map'])
    background = load_texture(background_filename)
    pass_map = PassMap(pg.image.load(str(pass_map_filename)))
    # TODO: load triggers from the room file
    triggers = [
        Trigger(
            pg.Rect(0, 0, 100, 100),
            {
                'enter': lambda: print('Enter'),
                'exit': lambda: print('Exit'),
            },
        ),
    ]
    return Room(background, pass_map, triggers)
