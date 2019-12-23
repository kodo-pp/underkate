import pygame as pg


class PassMap:
    def __init__(self, image: pg.Surface):
        self.image = image

    def collides(self, rect: pg.Rect) -> bool:
        self.image.lock()
        try:
            for y in range(rect.top, rect.bottom):
                for x in range(rect.left, rect.right):
                    red, *_ = self.image.get_at((x, y))
                    if red == 0:
                        return True
        finally:
            self.image.unlock()

        return False
