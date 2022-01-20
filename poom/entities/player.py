"""Describes player."""
from typing import Final, Sequence

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pygame.math import Vector2

from poom.entities.damagable import Damagable
from poom.viewer import Viewer


class Player(Damagable, Viewer):
    """Player."""

    max_health: Final[float] = 100
    movement_speed: Final[float] = 5
    rotation_speed: Final[float] = 0.3

    def __init__(
        self,
        *,
        map_: NDArray[np.float32],
        position: Vector2,
        angle: float,
        fov: float,
    ) -> None:
        super().__init__(position, angle, fov)
        self._map = map_
        self._health = self.max_health

    def update(self, dt: float) -> None:
        """Update player state.

        :param dt: delta time
        """
        self._process_keys(dt)
        self._process_mouse(dt)

    def take_damge(self, damage: float) -> None:
        """Decrease health.

        :param damage: damage by which health is reduced
        """
        self._health -= damage
        # TODO: process player death.

    def _move_direction(self, keys: Sequence[bool]) -> Vector2:
        """Calculate movement vector based on pressed keys and player view.

        Not normalize vector.

        :param keys: keys state
        :return: movement vector
        """
        directon = Vector2(0)
        if keys[pg.K_w]:
            directon += self.view_vector
        if keys[pg.K_s]:
            directon -= self.view_vector
        if keys[pg.K_a]:
            directon += self.view_vector.rotate(-90)  # noqa: WPS432 -90deg
        if keys[pg.K_d]:
            directon += self.view_vector.rotate(90)  # noqa: WPS432 90deg

        return directon

    def _process_keys(self, dt: float) -> None:
        """Process pressed keys and move player.

        :param dt: delta time
        """
        # Execute, while key is pressed, not single pushed
        keys = pg.key.get_pressed()
        direction = self._move_direction(keys)

        # ??? Should we fix faster movement on diagonal?
        new = self._position + direction * dt * self.movement_speed
        old = self._position

        if self._map[int(old.y), int(new.x)] == 0:  # noqa: WPS221
            self._position.x = new.x
        if self._map[int(new.y), int(old.x)] == 0:  # noqa: WPS221
            self._position.y = new.y

    def _process_mouse(self, dt: float) -> None:
        """Update player angle.

        :param dt: delta time
        """
        # FIXME: has side effects. Move to game classs
        x_movement, _ = pg.mouse.get_rel()
        self._angle += x_movement * self.rotation_speed * dt
