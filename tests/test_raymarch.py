import numpy as np
import pytest
from numpy.typing import NDArray

from poom.pooma.ray_march import shoot

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
        # Dont count (0; 0), but count (0; 1)
        pytest.param(0, 0, 0, 1, id="in wall"),
        pytest.param(1, 1, 0, 1, id="zero angle"),
        pytest.param(1, 1, np.pi / 4, 2 ** 0.5, id="pi/2 angle"),
    ],
)
def test_shoot(
    map_: Map,
    x0: float,
    y0: float,
    angle: float,
    expected: float,
) -> None:
    dist = shoot(map_, x0, y0, angle)
    assert dist == pytest.approx(expected)
