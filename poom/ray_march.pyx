#cython: language_level=3
from typing import List

import cython
import numpy as np
import pygame as pg

cimport numpy as np
from libc.math cimport cos, sin, sqrt, tan
from poom.math cimport Vec2f, Vec2i, frac, sign


cdef struct Intersection:
    float distance
    float offset
    char texture_index


# TODO: assert zero division
@cython.cdivision(True)
cdef Intersection ray_march(
    np.ndarray[np.int8_t, ndim=2] map_,
    float x0,
    float y0,
    float angle,
    float max_distance = 20.0,
):
    cdef float distance = 0, offset = 0
    cdef int is_vertical = 0

    cdef Vec2i direction = Vec2i(sign(cos(angle)), sign(sin(angle)))
    cdef float tangent = max(tan(angle) ** 2, 1e-6)
    # '1/tan(x) = cot(x)' and '(1 / x)^2 == 1 / x^2'
    cdef Vec2f ray_step = Vec2f(sqrt(1 + tangent), sqrt(1 + 1 / tangent))
    cdef Vec2i coords = Vec2i(<int>x0, <int>y0)
    # TODO: Looks like garbage... Rewrite it
    cdef Vec2f ray = Vec2f(
        (x0 - coords.x if direction.x < 0 else coords.x + 1 - x0) * ray_step.x,
        (y0 - coords.y if direction.y < 0 else coords.y + 1 - y0) * ray_step.y
    )

    while distance < max_distance:
        if ray.x < ray.y:
            coords.x += direction.x
            distance = ray.x
            ray.x += ray_step.x
            is_vertical = 0
        else:
            coords.y += direction.y
            distance = ray.y
            ray.y += ray_step.y
            is_vertical = 1

        # TODO: add wall descriptor
        if map_[coords.y, coords.x] != 0:  # Zero is empty cell
            offset = x0 + cos(angle) * distance if is_vertical else y0 + sin(angle) * distance
            return Intersection(distance, frac(offset), map_[coords.y, coords.x])
    return Intersection(max_distance, 0, -1)


# Ignore zero division errors due to performance reasons
# TODO: assert zero detalization
@cython.cdivision(True)
def draw_walls(
    np.ndarray[np.int8_t, ndim=2] map_,
    surface: pg.Surface,
    texture_vector: List[pg.Surface],
    float x0,
    float y0,
    float view,
    float fov,
) -> None:
    cdef size = surface.get_size()
    cdef int width = size[0], height = size[1]
    cdef int texture_width, texture_height

    cdef Intersection intersection
    cdef float alpha, angle
    cdef int half_height, offset, x

    for x in range(width):  # TODO: Can be parallel
        alpha = x / <float>width * fov
        angle = view - fov / 2 + alpha

        intersection = ray_march(map_, x0, y0, angle)
        # Zero index reversed for empty cell, so decrement index
        texture = texture_vector[intersection.texture_index - 1]
        texture_width, texture_height = texture.get_size()

        # TODO: fix parabola-like walls
        half_height = <int>(height / (intersection.distance * cos(angle - view))) // 2
        offset = <int>(texture_width * intersection.offset)

        line = texture.subsurface(offset, 0, 1, texture_height)
        wall = pg.transform.scale(line, (1, 2 * half_height))
        surface.blit(wall, (x, height // 2 - half_height))
