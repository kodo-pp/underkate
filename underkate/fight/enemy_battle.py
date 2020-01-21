from underkate.script import Script

from typing import Dict


class EnemyBattle:
    def __init__(self, scripts: Dict[str, Script]):
        self.scripts = scripts
        self.state: dict = {}


    def maybe_run_script(self, script_name: str, *args, **kwargs):
        if script_name in self.scripts:
            self.scripts[script_name](*args, state=self.state, **kwargs)
