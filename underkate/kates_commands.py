from underkate.animated_texture import load_animated_texture
from underkate.game_singletone import get_game
from underkate.managers import texture_manager, object_manager
from underkate.object import Object
from underkate.pending_callback_queue import get_pending_callback_queue
from underkate.room import load_room
from underkate.text import DisplayedText
from underkate.texture import Texture, load_texture
from underkate.vector import Vector

from typing import List, Optional, Dict, Callable

import pygame as pg  # type: ignore
from kates.runner import Runner, ExecutionStopReason


class ScriptError(Exception):
    pass


def _check(value: bool):
    if not value:
        raise ScriptError(f'Invalid command usage from katescript')


def kates_load_room(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 1)
    get_game().load_room(args[0])
    runner.execution_stop_reason = ExecutionStopReason('room_unload')
    return ''


def kates_load_texture(runner: Runner, args: List[str]) -> str:
    _check(1 <= len(args) <= 2)
    texture_path = get_game().room.path / args[0]
    if len(args) < 2:
        scale = 1
    else:
        scale = int(args[1])
    texture = load_texture(texture_path, scale)
    return texture_manager.add(texture, group=None)


def kates_create_object(runner: Runner, args: List[str]) -> str:
    _check(len(args) in (2, 3, 4, 8))
    x, y = map(float, args[:2])

    texture_id: Optional[str]
    if len(args) >= 3:
        texture_id = args[2]
    else:
        texture_id = None
    texture: Optional[Texture]
    if texture_id is None:
        texture = None
    else:
        texture = texture_manager[texture_id]

    is_passable: bool
    if len(args) >= 4:
        _check(args[3] in '01')
        is_passable = (args[3] == '1')
    else:
        is_passable = False

    hitbox: Optional[pg.Rect]
    if len(args) >= 8:
        x_center, y_center, width, height = map(int, args[4:8])
        hitbox = pg.Rect(0, 0, width, height)
        hitbox.center = (x_center, y_center)
    else:
        hitbox = None

    obj = Object(pos=Vector(x, y), texture=texture, is_passable=is_passable, hitbox=hitbox)
    get_game().room.add_object(obj)
    return object_manager.add(obj, group='current_room')


def kates_object_set_texture(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 2)
    object_id, texture_id = args
    object_manager[object_id].texture = texture_manager[texture_id]
    return ''


def kates_object_set_passable(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 2)
    object_id = args[0]
    _check(args[1] in '01')
    is_passable = (args[1] == '1')
    object_manager[object_id].is_passable = is_passable
    return ''


def kates_object_set_hitbox(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 5)
    object_id = args[0]
    x, y, w, h = map(int, args[1:5])
    hitbox = pg.Rect(0, 0, w, h)
    hitbox.center = (x, y)
    object_manager[object_id].hitbox = hitbox
    return ''


def kates_object_set_pos(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 3)
    object_id = args[0]
    x, y = map(float, args[1:3])
    pos = Vector(x, y)
    object_manager[object_id].pos = pos
    return ''


def kates_delete_object(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 1)
    object_id = args[0]
    object_manager[object_id].kill()
    return ''


def kates_sleep(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 1)
    delay = float(args[0])
    get_pending_callback_queue().fire_after(delay, runner.run)
    runner.execution_stop_reason = ExecutionStopReason('Zzz...')
    return ''


def kates_text(runner: Runner, args: List[str]) -> str:
    _check(len(args) == 1)
    serialized_text = args[0]
    text = DisplayedText.loads(serialized_text)
    text.on_finish_callback = runner.run
    text.initialize()
    get_game().spawn(text)
    return ''


FunctionType = Callable[[Runner, List[str]], str]


def get_command_list() -> Dict[str, FunctionType]:
    return {
        'create_object': kates_create_object,
        'delete_object': kates_delete_object,
        'load_room': kates_load_room,
        'load_texture': kates_load_texture,
        'object:set_hitbox': kates_object_set_hitbox,
        'object:set_passable': kates_object_set_passable,
        'object:set_pos': kates_object_set_pos,
        'object:set_texture': kates_object_set_texture,
        'sleep': kates_sleep,
        'text': kates_text,
    }
