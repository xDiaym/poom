import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, TypeVar

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.settings import ROOT
from poom.shared import Settings

T = TypeVar("T")
Map = NDArray[np.int8]

settings = Settings.load(ROOT)


def map2d(matrix: List[str], fn: Callable[[str], T]) -> List[List[T]]:
    result = []
    for line in matrix:
        result.append(list(map(fn, line)))
    return result


def load_map(path: Path) -> Map:
    with open(path, "r") as fp:
        text = fp.read().strip()
    string_list = text.split("\n")
    array = map2d(string_list, lambda x: 0 if x == "." else int(x))
    return np.array(array, dtype=np.int8)


def load_enemies_positions(path: Path) -> List[pg.Vector2]:
    with open(path, "r") as fp:
        raw_positions = json.load(fp)

    positions = []
    for position in raw_positions:
        # TODO: use dict.get()
        positions.append(pg.Vector2(position["x"], position["y"]))
    return positions


@dataclass
class Level:
    map_: Map
    enemies_positions: List[pg.Vector2]

    @classmethod
    def from_dir(cls, path: Path) -> "Level":
        map_ = load_map(path / "map.txt")
        positions = load_enemies_positions(path / "enemies.json")
        return cls(map_=map_, enemies_positions=positions)
