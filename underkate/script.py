from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text

import abc
import copy
from pathlib import Path
from types import CodeType
from typing import List, Callable, Any, Coroutine, Union, TYPE_CHECKING
from importlib.util import module_from_spec, spec_from_file_location

from memoization import cached  # type: ignore

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
    def __init__(self, module: Any, root: Path, function_name: str):
        self.module = module
        self.root = root
        self.function_name = function_name


    def __call__(self, *args, **kwargs) -> 'SuspendedPythonScript':
        return SuspendedPythonScript(getattr(self.module, self.function_name), self.root, args, kwargs)


class SuspendedPythonScript:
    def __init__(self, func: Callable, root: Path, args: Union[tuple, list], kwargs: dict):
        self.coro = func(*args, script=self, root=root, **kwargs)
        self()


    def __call__(self, arg: Any = None) -> bool:
        try:
            get_game().push_current_script(self)
            try:
                self.coro.send(arg)
                return False
            except StopIteration:
                return True
        finally:
            get_game().pop_current_script()


class SimpleScript(Script):
    def __init__(self, func: Callable):
        self.func = func


    def __call__(self, *args, **kwargs) -> SuspendedPythonScript:
        return SuspendedPythonScript(func=self.func, root=Path('.'), args=(), kwargs={})


class TextScript(Script):
    def __init__(self, text_name: str):
        self.text_name = text_name


    async def _run(self, *args, **kwargs):
        get_game().overworld.freeze()
        await display_text(load_text(self.text_name))
        get_game().overworld.unfreeze()


    def __call__(self, *args, **kwargs) -> SuspendedPythonScript:
        return SuspendedPythonScript(func=self._run, root=Path('.'), args=(), kwargs={})


@cached
def _raw_load_python_script(path: Path):
    spec = spec_from_file_location(f'<script:{str(path)}>', path)
    if spec is None or spec.loader is None:
        raise Exception(f'Failed to import script {str(path)}')
    module = module_from_spec(spec)
    # For some obscure reasons mypy doesn't seem to like this
    spec.loader.exec_module(module)  # type: ignore
    return module


def load_python_script(path: Path, function_name: str) -> PythonScript:
    return PythonScript(_raw_load_python_script(path), root=path.parent, function_name=function_name)


def load_script(script_identifier: str, root: Path) -> Script:
    # Script identifier must be in the form 'type::path'
    # TODO: verify this format compliance explicitly
    script_type, script_path = script_identifier.split('::', 1)

    if script_type == 'python':
        left, at, right = script_path.partition('@')
        if at == '':
            return load_python_script(root / left, 'main')
        else:
            return load_python_script(root / right, left)
    if script_type == 'room':
        return RoomScript(script_path)
    if script_type == 'text':
        return TextScript(script_path)

    raise Exception(f'Invalid script type: "{script_type}"')
