from underkate.overworld.pass_map import PassMap
from underkate.overworld.room import Room, Trigger, Event
from underkate.script import load_script
from underkate.texture import Texture, load_texture
from underkate.vector import Vector

from pathlib import Path
from typing import Union, List, Dict, Callable, Tuple, Any, Generator, cast

import pygame as pg  # type: ignore
import yaml


class RoomError(Exception):
    pass


class NoDefault:
    pass


def _get_item(
    data: dict,
    key: str,
    Type: type,
    default: Union[NoDefault, Any] = NoDefault()
) -> Any:
    if key not in data:
        if isinstance(default, NoDefault):
            raise RoomError(f'Missing required key: "{key}"')
        return default
    value = data[key]
    if not isinstance(value, Type):
        raise RoomError(f'Invalid type for "{key}": expected "{Type}", got "{type(value)}"')
    return value


def _load_room_data(path: Union[Path, str]) -> dict:
    if isinstance(path, str):
        path = Path(path)

    with open(path / 'room.yml') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise RoomError('Invalid room file format: expected a dictionary at the top level')
    return data


def _get_name(data: dict) -> str:
    return _get_item(data, 'name', str)


def _get_background(data: dict, root: Path) -> Texture:
    filename = _get_item(data, 'background', str)
    return load_texture(root / filename)


def _get_pass_map(data: dict, root: Path) -> PassMap:
    filename = _get_item(data, 'pass_map', str)
    return PassMap(pg.image.load(str(root / filename)))


def _get_triggers(data: dict, root: Path) -> List[Trigger]:
    return [
        _get_trigger(description, root)
        for description in _get_item(data, 'triggers', list, [])
    ]


def _get_trigger(trigger_description: dict, root: Path):
    # Left top corner coordinates and the dimensions (width and height)
    # TODO: proper validation here
    x, y, width, height = trigger_description['rect']
    hitbox = pg.Rect(x, y, width, height)

    def event_to_script_mapping_generator() -> Generator[Tuple[Event, Callable], None, None]:
        for event_name, script_identifier in _get_item(trigger_description, 'events', dict).items():
            if not isinstance(event_name, str):
                raise RoomError('Event name is not a string')
            if not isinstance(script_identifier, str):
                raise RoomError('Script identifier is not a string')
            yield Event(event_name), load_script(script_identifier, root=root)

    event_handlers = dict(event_to_script_mapping_generator())
    return Trigger(hitbox, event_handlers)


def load_room(path: Union[Path, str], prev_room_name: str) -> Room:
    if isinstance(path, str):
        path = Path(path)
    data = _load_room_data(path)
    room_name = _get_name(data)
    background = _get_background(data, path)
    pass_map = _get_pass_map(data, path)
    triggers = _get_triggers(data, path)

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
