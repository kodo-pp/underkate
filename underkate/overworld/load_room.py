from underkate.overworld.pass_map import PassMap
from underkate.overworld.room import Room, Trigger, Event
from underkate.script import load_script
from underkate.texture import load_texture
from underkate.vector import Vector

from pathlib import Path
from typing import Union, List, Dict, Callable, cast

import pygame as pg  # type: ignore
import yaml


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
