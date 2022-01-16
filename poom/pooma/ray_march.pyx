#cython: language_level=3
from typing import List

import cython
import numpy as np
import pygame as pg

cimport numpy as np
from libc.math cimport atan2, cos, sin, sqrt, tan

from poom.pooma.math cimport Vec2f, Vec2i, angle_diff, frac, magnitude, sign, sub


cdef struct Intersection:
    float distance
    float offset
    char texture_index


# TODO: assert zero division
@cython.cdivision(True)
cdef Intersection cast_wall(
    np.ndarray[np.int8_t, ndim=2] map_,
    Vec2f player,
    float angle,
    float max_distance = 20.0,
):
    cdef float distance = 0, offset = 0
    cdef int is_vertical = 0

    cdef Vec2i direction = Vec2i(sign(cos(angle)), sign(sin(angle)))
    cdef float tangent = max(tan(angle) ** 2, 1e-6)
    # '1/tan(x) = cot(x)' and '(1 / x)^2 == 1 / x^2'
    cdef Vec2f ray_step = Vec2f(sqrt(1 + tangent), sqrt(1 + 1 / tangent))
    cdef Vec2i coords = Vec2i(<int>player.x, <int>player.y)
    # TODO: Looks like garbage... Rewrite it
    cdef Vec2f ray = Vec2f(
        (player.x - coords.x if direction.x < 0 else coords.x + 1 - player.x) * ray_step.x,
        (player.y - coords.y if direction.y < 0 else coords.y + 1 - player.y) * ray_step.y
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
            offset = player.x + cos(angle) * distance if is_vertical else player.y + sin(angle) * distance
            return Intersection(distance, frac(offset), map_[coords.y, coords.x])
    return Intersection(max_distance, 0, -1)


# Ignore zero division errors due to performance reasons
# TODO: assert zero detalization
@cython.cdivision(True)
def draw_walls(
    np.ndarray[np.int8_t, ndim=2] map_,
    surface: pg.Surface,
    np.ndarray[np.float32_t, ndim=1] stencil,
    texture_vector: List[pg.Surface],
    float x0,
    float y0,
    float view,
    float fov,
) -> None:
    cdef:
        size = surface.get_size()
        int width = size[0], height = size[1]

    cdef:
        int texture_width, texture_height
        Intersection intersection
        float alpha, angle
        int half_height, offset, x

    for x in range(width):  # TODO: Can be parallel
        alpha = x / <float>width * fov
        angle = view - fov / 2 + alpha

        intersection = cast_wall(map_, Vec2f(x0, y0), angle)

        stencil[x] = intersection.distance
        # Zero index reversed for empty cell, so decrement index
        texture = texture_vector[intersection.texture_index - 1]
        texture_width, texture_height = texture.get_size()

        # TODO: fix parabola-like walls
        half_height = <int>(height / (intersection.distance * cos(angle - view))) // 2
        offset = <int>(texture_width * intersection.offset)

        line = texture.subsurface(offset, 0, 1, texture_height)
        wall = pg.transform.scale(line, (1, 2 * half_height))
        surface.blit(wall, (x, height // 2 - half_height))


@cython.cdivision(True)
def draw_sprite(
    surface: pg.Surface,
    np.ndarray[np.float32_t, ndim=1] stencil,
    texture: pg.Surface,
    float sprite_x,
    float sprite_y,
    float viewer_x,
    float viewer_y,
    float angle,
    float fov
):
    cdef:
        int surface_width = surface.get_width()
        int surface_height = surface.get_height()

    cdef:
        Vec2f v = sub(Vec2f(sprite_x, sprite_y), Vec2f(viewer_x, viewer_y))
        float distance = magnitude(v)
        float enemy_angle = atan2(v.y, v.x)
        float delta_a = angle_diff(enemy_angle, angle)

    cdef:
        float ratio = texture.get_width() / texture.get_height()
        int sprite_height = <int>(surface_height / magnitude(v))
        int sprite_width = <int>(sprite_height * ratio)
        int offset = <int>(
            surface_width / 2 + delta_a * surface_width / fov - sprite_width / 2
        )

    if offset + sprite_width < 0 or offset >= surface_width:
        # *ALL* sprite not in camera frustum, avoid scale and blit
        return

    scaled_texture = pg.transform.scale(texture, (sprite_width, sprite_height))
    cdef:
        int texture_offset = 0
    for texture_offset in range(<int>sprite_width):
        if offset + texture_offset < 0 or offset + texture_offset >= surface_width:
            # Part of sprite not in camera frustum, avoid scale and blit
            continue
        if stencil[offset + texture_offset] < distance:
            # Sprite behind something
            continue
        line = scaled_texture.subsurface((texture_offset, 0, 1, sprite_height))
        surface.blit(
            line,
            (<int> offset + texture_offset, (surface_height - <int> sprite_height) // 2)
        )
