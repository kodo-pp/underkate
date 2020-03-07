from underkate.fight.enemy_battle import EnemyBattle
from underkate.game_mode import GameMode
from underkate.global_game import get_game

import pygame as pg  # type: ignore


class Fight(GameMode):
    def __init__(self, enemy_battle: EnemyBattle):
        super().__init__(get_game())
        self.enemy_battle = enemy_battle


    def draw(self, destination: pg.Surface):
        self.enemy_battle.maybe_run_script('draw', destination=destination)
        super().draw(destination)


    def update(self, time_delta: float):
        self.enemy_battle.maybe_run_script('update', time_delta=time_delta)
        super().update(time_delta)


    def run(self):
        self.enemy_battle.run_script('run', enemy_battle=self.enemy_battle)
