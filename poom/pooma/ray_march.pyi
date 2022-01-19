from typing import List

import numpy as np
import pygame as pg
from numpy.typing import NDArray

def draw_walls(
    map_: NDArray[np.int8],
    surface: pg.Surface,
    stencil: NDArray[np.float32],
    texture: List[pg.Surface],
    x0: float,  # TODO: pass as vector
    y0: float,
    view: float,
    fov: float,
) -> None: ...
def draw_sprite(
    surface: pg.Surface,
    stencil: NDArray[np.float32],
    texture: pg.Surface,
    sprite_x: float,
    sprite_y: float,
    viewer_x: float,
    viewer_y: float,
    angle: float,
    fov: float,
) -> None: ...
def shoot(
    map_: NDArray[np.float32],
    x0: float,
    y0: float,
    angle: float,
    max_distance: float = 100.0,
) -> float: ...
