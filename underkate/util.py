from underkate.vector import Vector

from typing import Tuple


def clamp(x, minimum, maximum):
    if x < minimum:
        return minimum
    if x > maximum:
        return maximum
    return x


def collide_beam_and_point(
    beam: Tuple[Vector, Vector, float],
    point: Vector,
) -> bool:
    start, end, thickness = beam
    normal = (end - start).normal().normalized()
    offset = normal * (thickness / 2.0)
    line = end - start
    print(line, point - (start + offset), point - (start - offset))
    print(line.sin(point - (start + offset)), line.sin(point - (start - offset)))
    return line.sin(point - (start + offset)) * line.sin(point - (start - offset)) < 0
