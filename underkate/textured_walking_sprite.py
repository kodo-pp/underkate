from underkate.animated_texture import AnimatedTexture
from underkate.sprite import Sprite
from underkate.vector import Vector


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
