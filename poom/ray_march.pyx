#cython: language_level=3
import cython
import pygame as pg
import numpy as np

cimport numpy as np
from libc.math cimport cos, sin, sqrt

# TODO: check performance without numpy
cdef struct Vec2:
    float x
    float y


cdef float magnitude(Vec2 u, Vec2 v):
    cdef float dx = u.x - v.x
    cdef float dy = u.y - v.y
    return sqrt(dx * dx + dy * dy)


cdef float max(float a, float b):
    return a if a > b else b


cdef float frac(float x):
    return x - <int>x


# Ignore zero division errors due to performance reasons
# TODO: assert zero detalization
@cython.cdivision(True)
cdef Vec2 ray_march(
    np.ndarray[np.int8_t, ndim=2] map_,
    float x0,
    float y0,
    float angle,
    int detalization = 20,
):
    # FIXME: optimize
    cdef int max_size = 15
    cdef float step_x = cos(angle)
    cdef float step_y = sin(angle)
    cdef Vec2 p = Vec2(x0, y0)
    cdef float m = 0

    cdef int i = 0
    for i in range(max_size * detalization):
        m = i / <float> detalization
        p.x = x0 + step_x * m
        p.y = y0 + step_y * m
        if map_[<int>p.y, <int>p.x] != 0:  # TODO: add cell descriptor
            return p
    return Vec2(1e9, 1e9)


# Ignore zero division errors due to performance reasons
# TODO: assert zero detalization
@cython.cdivision(True)
def draw_wall_line(
    np.ndarray[np.int8_t, ndim=2] map_,
    surface: pg.Surface,
    texture: pg.Surface,
    float x0,
    float y0,
    float view,
    float fov,
    int detalization = 20
) -> None:
    cdef size = surface.get_size()
    cdef int width = size[0]
    cdef int height = size[1]
    cdef int texture_width = texture.get_size()[0]
    cdef int texture_height = texture.get_size()[1]

    cdef Vec2 p
    cdef float dist
    cdef float alpha, angle

    cdef int half_height, offset, x

    for x in range(width):
        alpha = x / <float>width * fov
        angle = view - fov / 2 + alpha

        p = ray_march(map_, x0, y0, angle)
        dist = magnitude(p, Vec2(x0, y0))

        # TODO: fix parabola-like walls
        half_height = <int>(height / <float>(dist * cos(angle - view))) // 2
        offset = <int>(texture_width * max(frac(p.x), frac(p.y)))
        line = texture.subsurface(offset, 0, 1, texture_height)
        wall = pg.transform.scale(line, (1, 2 * half_height))

        surface.blit(
            wall, (x, height // 2 - half_height)
        )
