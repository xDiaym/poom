import numpy as np
cimport numpy as np
from libc.math cimport sin, cos, sqrt



# TODO: check performance without numpy
# TODO: create Vec2 class/struct

cdef float magnitude(float x0, float y0, float x1, float y1):
    cdef float dx = x1 - x0
    cdef float dy = y1 - y0
    return sqrt(dx * dx + dy * dy)


def ray_march(
    np.ndarray[np.int8_t, ndim=2] map_,
    float x0,
    float y0,
    float angle,
    int detalization = 20,
) -> float:
    # FIXME: optimize
    cdef int max_size = 15
    cdef float step_x = cos(angle)
    cdef float step_y = sin(angle)
    cdef float px = x0
    cdef float py = y0
    cdef float m = 0

    cdef int i = 0
    for i in range(max_size * detalization):
        m = i / <float> detalization
        px = x0 + step_x * m
        py = y0 + step_y * m
        if map_[<int>py, <int>px] != 0:  # TODO: add cell descriptor
            return magnitude(x0, y0, px, py)
    return 1e6
