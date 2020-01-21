from underkate.fight.enemy_battle import EnemyBattle
from underkate.game_mode import GameMode

import pygame as pg  # type: ignore


class Fight(GameMode):
    def __init__(self, enemy_battle: EnemyBattle):
        self.enemy_battle = enemy_battle


    def draw(self, destination: pg.Surface):
        self.enemy_battle.maybe_run_script('draw', destination)
        super().draw(destination)


    def update(self, time_delta: float):
        self.enemy_battle.maybe_run_script('update', time_delta)
        super().update(time_delta)
