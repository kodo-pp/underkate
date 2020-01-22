from underkate.global_game import get_game

import abc
import copy
from pathlib import Path
from types import CodeType
from typing import List, Callable, Any, Coroutine, Union, TYPE_CHECKING
from importlib.util import module_from_spec, spec_from_file_location

if TYPE_CHECKING:
    from underkate.game import Game


class Script:
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class RoomScript(Script):
    def __init__(self, room_name: str):
        self.room_name = room_name


    def __call__(self, *args, **kwargs):
        get_game().overworld.load_room(self.room_name)


class PythonScript(Script):
    def __init__(self, module: Any, root: Path):
        self.module = module
        self.root = root


    def __call__(self, *args, **kwargs) -> 'SuspendedPythonScript':
        # TODO: export in-game API to scripts
        print(type(self.module))
        print(repr(self.module))
        print(dir(self.module))
        return SuspendedPythonScript(self.module.main, self.root, args, kwargs)


class SuspendedPythonScript:
    def __init__(self, func: Callable, root: Path, args: Union[tuple, list], kwargs: dict):
        self.coro = func(*args, script=self, root=root, **kwargs)
        self()


    def __call__(self, arg: Any = None) -> bool:
        try:
            self.coro.send(arg)
            return False
        except StopIteration:
            return True


def load_python_script(path: Path):
    spec = spec_from_file_location(f'<script:{str(path)}>', path)
    if spec is None or spec.loader is None:
        raise Exception(f'Failed to import script {str(path)}')
    module = module_from_spec(spec)
    # For some obscure reasons mypy doesn't seem to like this
    spec.loader.exec_module(module)  # type: ignore
    return PythonScript(module, root=path.parent)


def load_script(script_identifier: str, root: Path):
    # Script identifier must be in the form 'type::path'
    # TODO: verify this format compliance explicitly
    script_type, script_path = script_identifier.split('::', 1)

    if script_type == 'python':
        return load_python_script(root / script_path)
    if script_type == 'room':
        return RoomScript(script_path)

    raise Exception(f'Invalid script type: "{script_type}"')
