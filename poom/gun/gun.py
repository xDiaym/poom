"""Gun and his interface."""
from math import cos, radians, sin
from typing import Collection

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pygame.math import Vector2
from poom.entities import Pawn

from poom.pooma.ray_march import shoot


def vec_point_distance(
    start: Vector2,
    direction: Vector2,
    point: Vector2,
) -> float:
    """Calculate distance between point and vector.

    :param start: vector start point
    :param direction: direction
    :param point: point
    :return: distance between point and vector.
    """
    hypotenuse = point - start
    alpha = radians(hypotenuse.angle_to(direction))
    return hypotenuse.magnitude() * sin(alpha)


class Gun:
    """Weapon, that attacks on distance."""

    def __init__(
        self,
        level_map: NDArray[np.int8],
        delay: float,
        damage: float,
    ) -> None:
        """Initialize gun.

        :param level_map: level map
        :param delay: reload delay
        :param damage: gun damage
        """
        self._map = level_map
        self._delay = delay
        self._elapsed_time = delay
        self._damage = damage

    @property
    def can_shoot(self) -> bool:
        """Return true, if reload is complete."""
        return self._elapsed_time >= self._delay

    @property
    def reloading(self) -> bool:
        """Return true on reloading."""
        return self._elapsed_time < self._delay

    def can_cause_damage(
        self,
        position: pg.Vector2,
        angle: float,
        enemy: Pawn,
    ) -> bool:
        if not self.can_shoot:
            return False

        wall_distance = shoot(self._map, position.x, position.y, angle)
        view = Vector2(cos(angle), sin(angle))

        if wall_distance < (enemy.position - position).magnitude():
            # If enemy is behind wall
            return False

        distance = vec_point_distance(position, view, enemy.position)
        return abs(distance) < enemy.hitbox_width

    def shoot(
        self,
        position: Vector2,
        angle: float,
        enemies: Collection["Pawn"],
    ) -> None:
        """Shoot to enemies.

        :param position: shooter position
        :param angle: shooter angle
        :param enemies: enemies
        """
        if not self.can_shoot:
            return

        wall_distance = shoot(self._map, position.x, position.y, angle)
        view = Vector2(cos(angle), sin(angle))

        for enemy in enemies:
            if wall_distance < (enemy.position - position).magnitude():
                # If enemy is behind wall
                continue

            distance = vec_point_distance(position, view, enemy.position)
            if abs(distance) < enemy.hitbox_width:
                enemy.take_damage(self._damage)
        self._elapsed_time = 0

    def update(self, dt: float) -> None:
        """Update gun reload time.

        :param dt: delta time
        """
        self._elapsed_time += dt
