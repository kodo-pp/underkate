from underkate.script import Script, load_script

from pathlib import Path
from typing import Dict, Any

import yaml


class EnemyBattle:
    def __init__(self, scripts: Dict[str, Script], data: dict, root: Path):
        self.scripts = scripts
        self.state: dict = {}
        self.data = data
        self.root = root


    def maybe_run_script(self, script_name: str, *args, **kwargs):
        if script_name in self.scripts:
            self.scripts[script_name](*args, battle=self, **kwargs)


def load_enemy_battle(path: Path) -> EnemyBattle:
    data: Any = yaml.safe_load(path.read_bytes())
    scripts = {
        key: load_script(script_identifier, path)
        for key, script_identifier in data['scripts'].items()
    }
    return EnemyBattle(scripts, data, path)


def load_enemy_battle_by_name(name: str) -> EnemyBattle:
    return load_enemy_battle(Path('.') / 'assets' / 'enemies' / name)
