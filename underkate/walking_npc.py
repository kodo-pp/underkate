from underkate.event_manager import get_event_manager
from underkate.scriptlib.common import wait_for_event
from underkate.textured_walking_sprite import TexturedWalkingSprite
from underkate.vector import Vector


def sign(x):
    return -1 if x < 0 else 1


class WalkingNpc(TexturedWalkingSprite):
    def __init__(self, *, pos, left, right, front, back, speed):
        super().__init__(pos=pos, left=left, right=right, front=front, back=back, speed=speed)
        self._desired_position = None
        self._event_id = None
        self._is_alive = True


    async def walk_x(self, delta):
        self._desired_position = self.pos + Vector(delta, 0)
        self.set_moving(sign(delta), 0)
        self._event_id = get_event_manager().unique_id()
        await wait_for_event(self._event_id)


    async def walk_y(self, delta):
        self._desired_position = self.pos + Vector(0, delta)
        self.set_moving(0, sign(delta))
        self._event_id = get_event_manager().unique_id()
        await wait_for_event(self._event_id)


    def update(self, time_delta):
        super().update(time_delta)
        if self.__should_stop():
            self.set_moving(0, 0)
            self.pos = self._desired_position
            get_event_manager().raise_event(self._event_id, None)
            self._desired_position = None
            self._event_id = None


    def __should_stop(self):
        if self.moving_x != 0:
            return (self._desired_position.x - self.pos.x) * self.moving_x <= 0
        if self.moving_y != 0:
            return (self._desired_position.y - self.pos.y) * self.moving_y <= 0
        return False


    def is_alive(self):
        return self._is_alive


    def kill(self):
        self._is_alive = False
