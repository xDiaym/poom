import numpy as np
from numpy.typing import NDArray

def ray_march(
    map_: NDArray[np.int8],
    x0: float,
    y0: float,
    angle: float,
    detalization: int = 20,
) -> float: ...
