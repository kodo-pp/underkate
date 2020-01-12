from typing import List

import pygame as pg # type: ignore


class PassMap:
    def __init__(self, image: pg.Surface):
        self.image = image


    def is_passable(self, rect: pg.Rect) -> bool:
        # TODO: rewrite the algorithm or use JIT/AOT
        # compilation to speed it up in case optimization
        # is required

        clipped = rect.clip(self.image.get_rect())
        if rect != clipped:
            return False

        self.image.lock()
        try:
            for y in range(rect.top, rect.bottom):
                for x in range(rect.left, rect.right):
                    red, *_ = self.image.get_at((x, y))
                    if red == 0:
                        return False
        finally:
            self.image.unlock()

        return True
