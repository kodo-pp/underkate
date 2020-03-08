import math
from typing import Tuple, Callable


MappingFunction = Callable[[float], float]


class Mappings:
    @staticmethod
    def linear(x: float) -> float:
        return x


    @staticmethod
    def ease_out(x: float) -> float:
        return -x**2 + 2*x


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


    def dot(self, p: 'Vector') -> float:
        return self.x * p.x + self.y * p.y


    def sin(self, p: 'Vector') -> float:
        return self.x * p.y - self.y * p.x


    def __truediv__(self, k: float) -> 'Vector':
        return self * (1.0 / k)


    def __repr__(self) -> str:
        return f'Vector({self.x}, {self.y})'


    def length(self) -> float:
        return math.sqrt(self.dot(self))


    def normalized(self) -> 'Vector':
        length = self.length()
        if length < 1e-9:
            return Vector(1.0, 0.0)
        return self / length


    def normal(self) -> 'Vector':
        return Vector(self.y, -self.x)


    def interpolated(
        self,
        p: 'Vector',
        k: float,
        mapping: MappingFunction = Mappings.linear
    ) -> 'Vector':
        mapped_k = mapping(k)
        return self * (1.0 - mapped_k) + p * mapped_k


    def __neg__(self) -> 'Vector':
        return self * -1


    def ints(self) -> Tuple[int, int]:
        return round(self.x), round(self.y)
