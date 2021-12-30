from pathlib import Path
from typing import Callable, List, TypeVar

import numpy as np
from numpy.typing import NDArray

T = TypeVar("T")
Map = NDArray[np.int8]


def map2d(matrix: List[str], fn: Callable[[str], T]) -> List[List[T]]:
    result = []
    for line in matrix:
        result.append(list(map(fn, line)))
    return result


class MapLoader:
    def __init__(self, root: Path) -> None:
        self._root = root

    def as_list(self, number: int) -> List[str]:
        path = self._root / str(number) / "map.txt"
        with open(path) as fp:
            content = fp.read().strip()
        return content.split("\n")

    def as_numpy(self, number: int) -> NDArray[np.int8]:
        string_list = self.as_list(number)
        array = map2d(string_list, lambda x: 0 if x != "W" else 1)
        return np.array(array, dtype=np.int8)
