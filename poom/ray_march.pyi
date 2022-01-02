import numpy as np
from numpy.typing import NDArray
import pygame as pg


def draw_wall_line(
    map_: NDArray[np.uint8],
    surface: pg.Surface,
    texture: pg.Surface,
    x0: float,
    y0: float,
    view: float,
    fov: float,
    detalization: int = 20
) -> None:
    ...
