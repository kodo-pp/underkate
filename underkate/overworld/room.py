from underkate.script import Script, load_script
from underkate.object import Object
from underkate.overworld.pass_map import PassMap
from underkate.overworld.player import Player
from underkate.script import load_script
from underkate.texture import BaseTexture, load_texture
from underkate.vector import Vector
from underkate.wal_list import WalList

from pathlib import Path
from typing import Union, cast, Tuple, List, Dict, NewType, Callable, TYPE_CHECKING

import pygame as pg # type: ignore
import yaml

from loguru import logger

if TYPE_CHECKING:
    from underkate.game import Game


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
        scripts: Dict[str, Callable[[], None]],
        path: Path,
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


    def draw(self, surface: pg.Surface):
        x, y = surface.get_rect().center
        self.background.draw(surface, x, y)
        with self.objects:
            for obj in self.objects:
                obj.draw(surface)
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

        self.objects.filter(lambda x: x.is_alive())
        with self.objects:
            for obj in self.objects:
                obj.update()


    def add_object(self, obj: Object):
        logger.debug('Room.add_object({})', obj)
        self.objects.append(obj)


    def maybe_run_script(self, script_name: str):
        if script_name in self.scripts:
            self.scripts[script_name]()


class RoomError(Exception):
    pass


def load_room(path: Union[Path, str], prev_room_name: str) -> Room:
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
        for event_name, script_filename in cast(
            Dict[str, str],
            trigger_description['events']
        ).items():
            script = load_script(script_filename, root=path)
            event_handlers[Event(event_name)] = script

        triggers.append(
            Trigger(
                pg.Rect(x1, y1, width, height),
                event_handlers,
            ),
        )

    data_scripts = cast(Dict[str, str], data.get('scripts', {}))
    scripts = {
        script_name: load_script(script_identifier, root=path)
        for script_name, script_identifier in data_scripts.items()
    }

    initial_positions = cast(Dict[str, List[int]], data['initial_positions'])
    if prev_room_name in initial_positions:
        x, y = initial_positions[prev_room_name]
    else:
        x, y = initial_positions['default']
    player_position = Vector(x, y)

    return Room(
        name = room_name,
        background = background,
        pass_map = pass_map,
        triggers = triggers,
        scripts = scripts,
        player_position = player_position,
        path = path,
    )
