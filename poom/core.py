from pygame.math import Vector2

from poom.map import Map


def ray_march(
    map_: Map,
    position: Vector2,
    direction: Vector2,
    detalization: int = 20,
) -> float:
    # FIXME: optimize
    max_size = map_.size
    for i in range(max_size * detalization):
        pos = position + direction * (i / detalization)
        if map_.at(pos) == "W":  # TODO: create descriptors
            return (pos - position).length()
    return 1e6
