from underkate.event_manager import get_event_manager, EventId
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, wait_for_event

import abc
from pathlib import Path
from typing import List, Callable, Any, Union, Optional, TYPE_CHECKING
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
        return SuspendedPythonScript(
            getattr(self.module, self.function_name),
            self.root,
            args,
            kwargs,
        )


class SuspendedPythonScript:
    def __init__(self, func: Callable, root: Path, args: Union[tuple, list], kwargs: dict):
        self.coro = func(*args, script=self, root=root, **kwargs)
        self.finish_event: Optional[EventId] = get_event_manager().unique_id()
        self()


    def __call__(self, arg: Any = None) -> bool:
        try:
            get_game().push_current_script(self)
            try:
                self.coro.send(arg)
                return False
            except StopIteration:
                assert self.finish_event is not None
                get_event_manager().raise_event(self.finish_event, silent=True)
                self.finish_event = None
                return True
        finally:
            get_game().pop_current_script()


    def _has_completed(self) -> bool:
        return self.finish_event is None


    async def wait_until_completion(self) -> None:
        if self._has_completed():
            return
        await wait_for_event(self.finish_event)



class SimpleScript(Script):
    def __init__(self, func: Callable):
        self.func = func


    def __call__(self, *args, **kwargs) -> SuspendedPythonScript:
        return SuspendedPythonScript(func=self.func, root=Path('.'), args=(), kwargs={})


class TextScript(Script):
    def __init__(self, text_name: str):
        self.text_name = text_name


    async def _run(self, *args, **kwargs):
        del args, kwargs
        get_game().overworld.freeze()
        await display_text(load_text(self.text_name))
        get_game().overworld.unfreeze()


    def __call__(self, *args, **kwargs) -> SuspendedPythonScript:
        return SuspendedPythonScript(func=self._run, root=Path('.'), args=(), kwargs={})


class DynamicScript(Script):
    def __init__(self, selector: Callable[[], Union[List[str], str]], root: Path):
        self.selector = selector
        self.root = root


    def __call__(self, *args, **kwargs) -> Any:
        scripts = self.selector()
        if isinstance(scripts, str):
            scripts = [scripts]
        for script_name in scripts:
            load_script(script_name, self.root)(*args, **kwargs)


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
    return PythonScript(
        _raw_load_python_script(path),
        root = path.parent,
        function_name = function_name,
    )


def make_function_from_code(code: str) -> Callable:
    code = '\n'.join([
        'def __func():',
        '    from underkate.state import get_state',
        '    game = get_game()',
        '    room = game.overworld.room',
        '    state = get_state()',
        *['    ' + line for line in code.split('\n')],
    ])
    local_vars: dict = {}
    exec(code, globals(), local_vars)
    return local_vars['__func']


def load_dynamic_script(selector_code: str, root: Path) -> DynamicScript:
    selector = make_function_from_code(selector_code)
    return DynamicScript(selector, root)


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
    if script_type == 'dynamic':
        return load_dynamic_script(script_path, root)

    raise Exception(f'Invalid script type: "{script_type}"')
