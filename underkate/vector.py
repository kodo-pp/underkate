from typing import Tuple


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def is_zero(self, eps: float = 1e-9) -> bool:
        return abs(self.x) + abs(self.y) < eps

    def __add__(self, p: 'Vector') -> 'Vector':
        return Vector(self.x + p.x, self.y + p.y)

    def __sub__(self, p: 'Vector') -> 'Vector':
        return Vector(self.x - p.x, self.y - p.y)

    def __mul__(self, k: float) -> 'Vector':
        return Vector(self.x * k, self.y * k)

    def __truediv__(self, k: float) -> 'Vector':
        return self * (1.0 / k)

    def __neg__(self) -> 'Vector':
        return self * -1

    def ints(self) -> Tuple[int, int]:
        return round(self.x), round(self.y)
