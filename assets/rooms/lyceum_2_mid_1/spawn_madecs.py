from underkate.animated_texture import load_animated_texture
from underkate.global_game import get_game
from underkate.scriptlib.common import sleep
from underkate.vector import Vector
from underkate.walking_npc import WalkingNpc

from pathlib import Path

import pygame as pg


class Madec(WalkingNpc):
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
        super().update(time_delta)

        self._time_since_birth += time_delta
        if self._time_since_birth > self.lifetime:
            self.kill()
            return

        if self.is_touching_player():
            print('Ouch!')


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
        get_game().overworld.room.spawn(
            Madec(
                pos = self.position,
                speed = self.speed.length(),
                direction = self.speed.normalized(),
                lifetime = 10.0,
                manager = self.manager,
            ),
        )


class Manager:
    def __init__(self):
        self.spawners = []


    def add_spawner(self, **kwargs):
        self.spawners.append(Spawner(**kwargs, manager=self))


    def update(self, time_delta):
        for s in self.spawners:
            s.update(time_delta)


async def main(**kwargs):
    manager = Manager()
    manager.add_spawner(position=Vector(1105, 179), speed=Vector(-120, 120), interval=1.5)
    manager.add_spawner(position=Vector(-101, 894), speed=Vector(130, -140), interval=1.0)
    manager.add_spawner(position=Vector(969, 1012), speed=Vector(-200, -200), interval=0.7)
    get_game().overworld.room.add_update_callback(manager.update)
