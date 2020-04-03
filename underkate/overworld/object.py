from underkate.event_manager import get_event_manager, Subscriber
from underkate.global_game import get_game
from underkate.sprite import Sprite
from underkate.texture import BaseTexture
from underkate.vector import Vector

from typing import Optional, Callable, Any

import pygame as pg  # type: ignore


def generate_hitbox(width: int, height: int) -> pg.Rect:
    hitbox = pg.Rect(0, 0, width, height)
    hitbox.center = (0, 0)
    return hitbox


class Object(Sprite):
    def __init__(
        self,
        pos: Vector,
        texture: Optional[BaseTexture] = None,
        is_passable: bool = False,
        hitbox: Optional[pg.Rect] = None,
    ):
        super().__init__(pos)
        self.texture = texture
        self.is_passable = is_passable
        self.hitbox = hitbox if hitbox is not None else generate_hitbox(20, 20)
        get_event_manager().subscribe('key:confirm', Subscriber(self._on_interact_somewhere))
        self.on_interact: Callable[[], Any] = lambda: None


    def __repr__(self) -> str:
        # Not a tuple, but literal string concatenation instead
        return (
            f'Object(pos: {self.pos.ints()}, '
            f'texture: {self.texture}, '
            f'passable: {self.is_passable}, '
            f'hitbox: {self.hitbox}, '
            f'alive: {self._is_alive})'
        )


    def update(self):
        pass


    def draw(self, surface: pg.Surface):
        if self.texture is None:
            return
        x, y = self.pos.ints()
        self.texture.draw(surface, x, y)


    def get_hitbox_with_position(self) -> pg.Rect:
        x, y = self.pos.ints()
        return self.hitbox.move(x, y)


    def can_player_pass(self, player_position: pg.Rect) -> bool:
        return self.is_passable or not bool(
            self.get_hitbox_with_position().colliderect(player_position)
        )


    def _on_interact_somewhere(self, *args):
        del args
        if not self.is_alive():
            return
        if not get_game().overworld.is_frozen():
            player = get_game().overworld.room.player
            if self.get_hitbox_with_position().colliderect(player.get_extended_hitbox()):
                self.on_interact()
        get_event_manager().subscribe('key:confirm', Subscriber(self._on_interact_somewhere))
