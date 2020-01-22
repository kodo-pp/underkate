from underkate.script import Script, load_script

from pathlib import Path
from typing import Dict, Any

import yaml


class EnemyBattle:
    def __init__(self, scripts: Dict[str, Script], data: dict):
        self.scripts = scripts
        self.state: dict = {}
        self.data = data


    def maybe_run_script(self, script_name: str, *args, **kwargs):
        if script_name in self.scripts:
            self.scripts[script_name](*args, battle=self, **kwargs)


def load_enemy_battle(path: Path) -> EnemyBattle:
    data: Any = yaml.safe_load(path.read_bytes())
    scripts = {
        key: load_script(script_identifier, path)
        for key, script_identifier in data['scripts'].items()
    }
    return EnemyBattle(scripts, data)
