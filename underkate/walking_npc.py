from underkate.event_manager import get_event_manager, EventId
from underkate.scriptlib.common import wait_for_event
from underkate.textured_walking_sprite import TexturedWalkingSprite
from underkate.vector import Vector

from typing import Optional


class WalkingNpc(TexturedWalkingSprite):
    def __init__(self, *, pos, left, right, front, back, speed):
        super().__init__(pos=pos, left=left, right=right, front=front, back=back, speed=speed)
        self._stop_event: Optional[EventId] = None
        self._is_alive = True
        self._target: Optional[Vector] = None


    async def walk(self, delta: Vector):
        assert self._target is None
        self._target = self.pos + delta

        direction = delta.normalized()
        self.set_moving(direction.x, direction.y)

        self._stop_event = get_event_manager().unique_id()
        await wait_for_event(self._stop_event)

        self.set_moving(0, 0)
        self.pos = self._target
        self._target = None


    async def walk_x(self, delta: float):
        await self.walk(Vector(delta, 0))


    async def walk_y(self, delta: float):
        await self.walk(Vector(0, delta))


    def _is_walking(self) -> bool:
        return self._target is not None


    def update(self, time_delta: float):
        super().update(time_delta)
        if self._is_walking() and self._should_stop():
            assert self._stop_event is not None
            get_event_manager().raise_event(self._stop_event, None)
            self._stop_event = None


    def _should_stop(self) -> bool:
        assert self._target is not None
        vec_current = self._target - self.pos
        next_pos = self.pos + self.get_movement_direction() * self.speed * 1e-2
        vec_next = self._target - next_pos
        return vec_next.length_sq() >= vec_current.length_sq()


    def is_alive(self) -> bool:
        return self._is_alive


    def kill(self):
        self._is_alive = False
