from underkate.animated_texture import load_animated_texture
from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.script import SimpleScript
from underkate.scriptlib.common import sleep
from underkate.scriptlib.fight import fight
from underkate.vector import Vector
from underkate.wal_list import WalList
from underkate.textured_walking_sprite import TexturedWalkingSprite

import random as rd
from pathlib import Path

import pygame as pg


class Madec(TexturedWalkingSprite):
    def __init__(self, pos, speed, direction, lifetime, manager):
        texture = load_animated_texture(
            Path('.') / 'assets' / 'textures' / 'madec' / 'overworld',
            scale = 2,
        )

        super().__init__(
            pos = pos,
            left = texture,
            right = texture,
            front = texture,
            back = texture,
            speed = speed,
        )
        self.lifetime = lifetime
        self._time_since_birth = 0.0
        self.manager = manager
        self.set_moving(direction.x, direction.y)


    def is_touching_player(self):
        x, y = self.pos.ints()
        rect = self.hitbox.move(x, y)
        player_rect = get_game().overworld.room.player.get_hitbox_with_position()
        return bool(rect.colliderect(player_rect))


    def update(self, time_delta):
        if self.manager.is_frozen():
            return
        super().update(time_delta)

        self._time_since_birth += time_delta
        if self._time_since_birth > self.lifetime:
            self.kill()
            return

        if self.is_touching_player() and not get_game().overworld.is_frozen():
            enemy_name = rd.choice(['algebroid', 'geoma'])

            async def func(*a, **k):
                async def clear():
                    self.manager.clear()

                get_game().overworld.freeze()
                await fight(load_enemy_battle_by_name(enemy_name), on_after_enter=clear)
                get_game().overworld.unfreeze()

            script = SimpleScript(func)
            self.manager.freeze()
            script()


    hitbox = pg.Rect(-20, -40, 40, 80)


class Spawner:
    def __init__(self, position, speed, interval, manager):
        self.position = position
        self.speed = speed
        self.interval = interval
        self._time_since_last_spawn = 0.0
        self.manager = manager


    def update(self, time_delta):
        self._time_since_last_spawn += time_delta
        if self._time_since_last_spawn >= self.interval:
            self._spawn()
            self._time_since_last_spawn = 0.0


    def _spawn(self):
        madec = Madec(
            pos = self.position,
            speed = self.speed.length(),
            direction = self.speed.normalized(),
            lifetime = 10.0,
            manager = self.manager,
        )
        get_game().overworld.room.spawn(madec)
        self.manager.register(madec)


class SpawnerManager:
    def __init__(self):
        self.spawners = WalList([])
        self.madecs = WalList([])
        self._is_frozen = False


    def add_spawner(self, **kwargs):
        self.spawners.append(Spawner(**kwargs, manager=self))


    def register(self, madec):
        self.madecs.append(madec)


    def freeze(self):
        self._is_frozen = True


    def unfreeze(self):
        self._is_frozen = False


    def is_frozen(self):
        return self._is_frozen


    def kill_all(self):
        with self.madecs:
            for madec in self.madecs:
                madec.kill()

        self.madecs.filter(lambda x: False)


    def clear(self):
        self.kill_all()
        self.unfreeze()


    def update(self, time_delta):
        with self.spawners:
            for s in self.spawners:
                s.update(time_delta)

        self.madecs.filter(lambda x: x.is_alive())


async def setup(manager: SpawnerManager):
    get_game().overworld.room.add_update_callback(manager.update)
