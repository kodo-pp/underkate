import abc
import copy
from pathlib import Path
from types import CodeType
from typing import List, Callable, TYPE_CHECKING

import kates.parser
import kates.runner

if TYPE_CHECKING:
    from underkate.game import Game


class Script:
    @abc.abstractmethod
    def __call__(self):
        ...


class PythonScript(Script):
    def __init__(self, compiled_code: CodeType, game: 'Game'):
        self.compiled_code = compiled_code
        self.game = game


    def __call__(self):
        local_vars = {
            'game': self.game,
        }
        exec(self.compiled_code, globals(), local_vars)


class KateScript(Script):
    def __init__(self, runner: kates.runner.Runner, game: 'Game'):
        self.runner = runner
        self.game = game


    def __call__(self):
        copy.deepcopy(self.runner).run()


def load_python_script(path: Path, game: 'Game'):
    code = path.read_bytes()
    compiled_code = compile(code, str(path), 'exec')
    return PythonScript(compiled_code, game)


def load_kate_script(path: Path, game: 'Game'):
    from underkate.kates_commands import get_command_list
    code = path.read_text()
    functions = get_command_list()
    script = kates.runner.Script(kates.parser.parse(code))
    runner = kates.runner.Runner(functions=functions, script=script)
    return KateScript(runner, game)


def load_script(path: Path, game: 'Game'):
    suffix = path.suffix
    if suffix == '.py':
        return load_python_script(path, game)
    if suffix == '.kates':
        return load_kate_script(path, game)
    raise Exception(f'Invalid script file extension: {repr(suffix)}')
