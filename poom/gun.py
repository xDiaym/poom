"""Gun and animated gun. Used for attacking."""
from imp import reload
from math import cos, radians, sin
from pathlib import Path
from typing import Collection

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pygame.math import Vector2

from poom.animated import Animation
from poom.entities import Pawn, Renderable
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

    def shoot(
        self,
        position: Vector2,
        angle: float,
        enemies: Collection[Pawn],
    ) -> None:
        """Shoot to enemies.

        :param position: shooter position
        :param angle: shooter angle
        :param enemies: enemies
        """
        if not self.can_shoot:
            return

        wall_distance = shoot(self._map, *position, angle)
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


class AnimatedGun(Renderable):
    """Gun with texture and reload animation.

    Used as player gun.
    """

    def __init__(self, gun: Gun, animation: Animation) -> None:
        """Initialize animated gun.

        :param gun: gun instance
        :param animation: gun animation
        """
        self._gun = gun
        self._animation = animation

    def shoot(
        self,
        position: Vector2,
        angle: float,
        enemies: Collection[Pawn],
    ) -> None:
        """Shoot to enemies.

        :param position: shooter position
        :param angle: shooter angle
        :param enemies: enemies
        """
        self._gun.shoot(position, angle, enemies)

    @property
    def texture(self) -> pg.Surface:
        """Return gun texture."""
        return self._animation.current_frame

    def update(self, dt: float) -> None:
        """Update gun texture.

        :param dt: delta time
        """
        self._gun.update(dt)
        if self._gun.reloading:
            self._animation.update(dt)
        else:
            self._animation.reset()


def create_animated_gun(
    level_map: NDArray[np.int8],
    reload_time: float,
    damage: float,
    animation_path: Path,
    scale: float,
) -> AnimatedGun:
    gun = Gun(level_map, reload_time, damage)
    animation = Animation.from_dir(animation_path, reload_time, scale)
    return AnimatedGun(gun, animation)
