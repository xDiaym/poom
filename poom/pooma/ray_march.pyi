from typing import List

import numpy as np
import pygame as pg
from numpy.typing import NDArray

def draw_walls(
    map_: NDArray[np.int8],
    surface: pg.Surface,
    stencil: NDArray[np.float],
    texture: List[pg.Surface],
    x0: float,
    y0: float,
    view: float,
    fov: float,
) -> None: ...
