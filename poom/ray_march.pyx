#cython: language_level=3
import cython
import numpy as np
import pygame as pg

cimport numpy as np
from libc.math cimport cos, sin, sqrt, tan


cdef float frac(float x):
    return x - <int>x

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

cdef float magnitude(Vec2f u, Vec2f v):
    cdef float dx = u.x - v.x
    cdef float dy = u.y - v.y
    return sqrt(dx * dx + dy * dy)


cdef struct Intersection:
    float distance
    float offset


# TODO: assert zero division
@cython.cdivision(True)
cdef Intersection ray_march(
    np.ndarray[np.int8_t, ndim=2] map_,
    float x0,
    float y0,
    float angle,
    float max_distance = 20.0,
):
    cdef float distance = 0
    cdef int is_vertical = 0

    cdef Vec2i direction = Vec2i(sign(cos(angle)), sign(sin(angle)))
    cdef float tangent = sqr(tan(angle)) or 1e-6
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

        if map_[coords.y, coords.x] == 1:
            return Intersection(
                distance,
                frac(
                    y0 + sin(angle) * distance if is_vertical == 0
                    else x0 + cos(angle) * distance
                )
            )
    return Intersection(max_distance, 0)


# Ignore zero division errors due to performance reasons
# TODO: assert zero detalization
@cython.cdivision(True)
def draw_walls(
    np.ndarray[np.int8_t, ndim=2] map_,
    surface: pg.Surface,
    texture: pg.Surface,
    float x0,
    float y0,
    float view,
    float fov,
) -> None:
    cdef size = surface.get_size()
    cdef int width = size[0]
    cdef int height = size[1]
    cdef int texture_width = texture.get_size()[0]
    cdef int texture_height = texture.get_size()[1]

    cdef Intersection intersection
    cdef float alpha, angled

    cdef int half_height, offset, x

    for x in range(width):  # TODO: Can be parallel
        alpha = x / <float>width * fov
        angle = view - fov / 2 + alpha

        intersection = ray_march(map_, x0, y0, angle)

        # TODO: fix parabola-like walls
        half_height = <int>(height / (intersection.distance * cos(angle - view))) // 2
        offset = <int>(texture_width * intersection.offset)

        line = texture.subsurface(offset, 0, 1, texture_height)
        wall = pg.transform.scale(line, (1, 2 * half_height))
        surface.blit(wall, (x, height // 2 - half_height))
