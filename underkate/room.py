from . import script
from .object import Object
from .pass_map import PassMap
from .player import Player
from .texture import BaseTexture, load_texture
from .vector import Vector

from pathlib import Path
from typing import Union, cast, Tuple, List, Dict, NewType, Callable, TYPE_CHECKING

import pygame as pg # type: ignore
import yaml

from loguru import logger

if TYPE_CHECKING:
    from .game import Game


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
        initial_positions: Dict[str, Vector],
        on_load: Callable,
        path: Path,
    ):
        self.name = name
        self.background = background
        self.pass_map = pass_map
        self.trigger_event_watchers = [
            TriggerEventWatcher(trigger)
            for trigger in triggers
        ]
        self.initial_positions = initial_positions
        self.on_load = on_load
        self.objects: List[Object] = []
        self.path = path


    def draw(self, surface: pg.Surface):
        x, y = surface.get_rect().center
        self.background.draw(surface, x, y)
        for obj in self.objects:
            obj.draw(surface)


    def is_passable(self, rect: pg.Rect) -> bool:
        return self.pass_map.is_passable(rect) and all(
            obj.can_player_pass(rect)
            for obj in self.objects
        )


    def get_size(self) -> Tuple[int, int]:
        rect = self.pass_map.image.get_rect()
        return rect.width, rect.height


    def update(self, player: Player):
        for watcher in self.trigger_event_watchers:
            events = watcher.update(player)
            for event in events:
                watcher.pass_event(event)

        alive_objects = [obj for obj in self.objects if obj.is_alive()]
        self.objects = alive_objects

        for obj in self.objects:
            obj.update()


    def add_object(self, obj: Object):
        logger.debug('Room.add_object({})', obj)
        self.objects.append(obj)


class RoomError(Exception):
    pass


def load_room(path: Union[Path, str], game: 'Game') -> Room:
    if isinstance(path, str):
        path = Path(path)

    with open(path / 'room.yml') as f:
        data = yaml.safe_load(f)

    room_name = cast(str, data['name'])
    background_filename = path / cast(str, data['background'])
    pass_map_filename = path / cast(str, data['pass_map'])
    background = load_texture(background_filename)
    pass_map = PassMap(pg.image.load(str(pass_map_filename)))

    triggers: List[Trigger] = []

    for trigger_description in data['triggers']:
        x1, y1, width, height = trigger_description['rect']
        if width < 0 or height < 0:
            raise RoomError('Height or width of a trigger is negative')

        event_handlers: Dict[Event, Callable] = {}
        for event_name, raw_script_filename in trigger_description['events'].items():
            script_filename = path / cast(str, raw_script_filename)
            script_object = script.load_script(script_filename, game)
            event_handlers[Event(event_name)] = script_object

        triggers.append(
            Trigger(
                pg.Rect(x1, y1, width, height),
                event_handlers,
            ),
        )

    if 'on_load' in data:
        on_load = script.load_script(path / data['on_load'], game)
    else:
        on_load = lambda: None

    initial_positions = {
        name: Vector(x, y)
        for (name, [x, y]) in data['initial_positions'].items()
    }

    return Room(
        name = room_name,
        background = background,
        pass_map = pass_map,
        triggers = triggers,
        on_load = on_load,
        initial_positions = initial_positions,
        path = path,
    )
