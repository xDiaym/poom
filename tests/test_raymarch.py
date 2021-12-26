import numpy as np
import pytest
from numpy.typing import NDArray

from poom.ray_march import ray_march

Map = NDArray[np.int8]


@pytest.fixture
def map_() -> Map:
    return np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.int8,
    )


@pytest.mark.parametrize(
    "x0, y0, angle, expected",
    [
        pytest.param(0, 0, 0, 0, id="in wall"),
        pytest.param(1, 1, 0, 1, id="zero angle"),
        pytest.param(1, 1, np.pi / 4, 2 ** 0.5, id="pi/2 angle"),
    ],
)
def test_ray_march(
    map_: Map, x0: float, y0: float, angle: float, expected: float
) -> None:
    dist = ray_march(map_, x0, y0, angle)
    assert dist == pytest.approx(expected, 0.1)
