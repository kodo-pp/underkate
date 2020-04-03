from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def script_import(module_name: str, *, file: str, name: str):
    path_to_import = Path(file).parent / f'{module_name}.py'
    script_module_name = f'{name}.{module_name}'
    spec = spec_from_file_location(script_module_name, path_to_import)
    if spec is None or spec.loader is None:
        raise Exception(f'Failed to import script module {script_module_name}')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module
