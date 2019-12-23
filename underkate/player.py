from .textured_walking_sprite import TexturedWalkingSprite
from .animation import load_animation
from .vector import Vector


_player = None


def get_player():
    global _player

    if _player is None:
        _player = TexturedWalkingSprite(
            pos = Vector(100, 100),
            left = load_animation('assets/player/left', 4),
            right = load_animation('assets/player/right', 4),
            front = load_animation('assets/player/front', 4),
            back = load_animation('assets/player/back', 4),
            speed = 160.0,
        )
    return _player
