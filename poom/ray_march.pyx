#cython: language_level=3
import cython
import numpy as np

cimport numpy as np
from libc.math cimport tan, sqrt, cos, sin

cdef int sign(float x):
    return 1 if x >= 0 else -1

cdef float sqr(float x):
    return x * x

cdef struct Vec2i:
    int x
    int y

cdef struct Vec2f:
    float x
    float y

cdef float magnitude(float x0, float y0, float x1, float y1):
    cdef float dx = x1 - x0
    cdef float dy = y1 - y0
    return sqrt(dx * dx + dy * dy)


@cython.cdivision(True)
def ray_march(
    np.ndarray[np.int8_t, ndim=2] map_,
    float x0,
    float y0,
    float angle,
    float max_distance = 35.0,
) -> float:
    # FIXME: optimize
    cdef float distance = 0
    cdef Vec2i direction = Vec2i(sign(cos(angle)), sign(sin(angle)))
    cdef float tangent = sqr(tan(angle)) or 1e-6
    # '1/tan(x) = cot(x)' and '(1 / x)^2 == 1 / x^2'
    cdef Vec2f ray_step = Vec2f(sqrt(1 + tangent), sqrt(1 + 1 / tangent))
    cdef Vec2i coords = Vec2i(<int>x0, <int>y0)
    cdef Vec2f ray = Vec2f(
        (x0 - coords.x if direction.x < 0 else coords.x + 1 - x0) * ray_step.x,
        (y0 - coords.y if direction.y < 0 else coords.y + 1 - y0) * ray_step.y
    )

    while distance < max_distance:
        if ray.x < ray.y:
            coords.x += direction.x
            distance = ray.x
            ray.x += ray_step.x
        else:
            coords.y += direction.y
            distance = ray.y
            ray.y += ray_step.y

        if map_[coords.y, coords.x] == 1:
            return distance
    return max_distance
