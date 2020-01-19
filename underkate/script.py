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
    def __init__(self, compiled_code: CodeType):
        self.compiled_code = compiled_code


    def __call__(self):
        # TODO: export in-game API to scripts
        exec(self.compiled_code, globals(), {})


class KateScript(Script):
    def __init__(self, runner: kates.runner.Runner):
        self.runner = runner


    def __call__(self):
        copy.deepcopy(self.runner).run()


def load_python_script(path: Path):
    code = path.read_bytes()
    compiled_code = compile(code, str(path), 'exec')
    return PythonScript(compiled_code)


def load_kate_script(path: Path):
    from underkate.kates_commands import get_command_list

    # Read and parse the script
    code = path.read_text()
    script = kates.runner.Script(kates.parser.parse(code))

    # Prepare in-game API bindings
    functions = get_command_list()

    # Prepare an interpreter instance for this script
    runner = kates.runner.Runner(functions=functions, script=script)
    return KateScript(runner)


def load_script(script_identifier: str, root: Path):
    # Script identifier must be in the form 'type::path'
    # TODO: verify this format compliance explicitly
    script_type, script_path = script_identifier.split('::', 1)

    if script_type == 'python':
        return load_python_script(root / script_path)
    if script_type == 'kates':
        return load_kate_script(root / script_path)

    raise Exception(f'Invalid script type: "{script_type}"')
