from functools import cached_property
from math import ceil
from typing import List

from pygame.math import Vector2


class Map:
    def __init__(self, map_: List[str]) -> None:
        assert len(map_) > 0, "Empty map"
        self._map = map_

    def at(self, position: Vector2) -> str:
        return self._map[int(position.y)][int(position.x)]

    @cached_property
    def size(self) -> int:
        diag = Vector2(len(self._map), len(self._map[0]))
        return ceil(diag.length())
