from underkate.animated_texture import AnimatedTexture
from underkate.event_manager import get_event_manager, EventId
from underkate.scriptlib.common import wait_for_event
from underkate.sprite import Sprite
from underkate.vector import Vector

from typing import Optional


def clamp(a, b, x):
    return min(max(a, x), b)


class TexturedWalkingSprite(Sprite):
    def __init__(
        self,
        pos: Vector,
        left: AnimatedTexture,
        right: AnimatedTexture,
        front: AnimatedTexture,
        back: AnimatedTexture,
        speed: float,
    ):
        super().__init__(pos)
        self.left = left
        self.right = right
        self.front = front
        self.back = back
        self.speed = speed
        self.direction = 'right'
        self.moving_x = 0
        self.moving_y = 0
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


    def _should_stop(self) -> bool:
        assert self._target is not None
        vec_current = self._target - self.pos
        next_pos = self.pos + self.get_movement_direction() * self.speed * 1e-2
        vec_next = self._target - next_pos
        return vec_next.length_sq() >= vec_current.length_sq()


    def start_moving_x(self, x):
        self.moving_x += x
        self.moving_x = clamp(-1, 1, self.moving_x)
        self.update_direction()


    def stop_moving_x(self, x):
        self.start_moving_x(-x)


    def start_moving_y(self, y):
        self.moving_y += y
        self.moving_y = clamp(-1, 1, self.moving_y)
        self.update_direction()


    def stop_moving_y(self, y):
        self.start_moving_y(-y)


    def set_moving(self, x, y):
        self.moving_x = x
        self.moving_y = y
        self.update_direction()


    def update_direction(self):
        if self.moving_x == 1:
            self.direction = 'right'
        elif self.moving_x == -1:
            self.direction = 'left'
        elif self.moving_y == 1:
            self.direction = 'down'
        elif self.moving_y == -1:
            self.direction = 'up'


    def is_moving(self):
        return any((self.moving_x != 0, self.moving_y != 0))


    def update(self, time_delta):
        delta = Vector(self.moving_x, self.moving_y) * (self.speed * time_delta)
        self.move(delta)
        if self._is_walking() and self._should_stop():
            assert self._stop_event is not None
            get_event_manager().raise_event(self._stop_event, None)
            self._stop_event = None


    def move(self, delta):
        self.pos += delta


    def get_current_texture(self):
        if self.direction == 'right':
            return self.right
        elif self.direction == 'left':
            return self.left
        elif self.direction == 'up':
            return self.back
        elif self.direction == 'down':
            return self.front
        else:
            raise Exception('Invalid direction: ' + repr(self.direction))


    def draw(self, destination):
        x, y = self.pos.ints()
        if self.is_moving():
            self.get_current_texture().draw(destination, x, y)
        else:
            self.get_current_texture().draw(destination, x, y, force_frame=0)


    def get_movement_direction(self) -> Vector:
        return Vector(self.moving_x, self.moving_y)
