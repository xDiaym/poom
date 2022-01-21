"""Describes player."""
from typing import Final, List, Sequence

import numpy as np
import pygame as pg
from pygame.event import Event
from numpy.typing import NDArray
from pygame.math import Vector2

from poom.entities.damagable import Damagable
from poom.viewer import Viewer


class Player(Damagable, Viewer):
    """Player."""

    max_health: Final[float] = 100
    movement_speed: Final[float] = 5
    rotation_speed: Final[float] = 3

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

    def update(self, dt: float, event: List[Event]) -> None:
        """Update player state.

        :param dt: delta time
        """
        self._process_keys(dt)

    def take_damge(self, damage: float) -> None:
        """Decrease health.

        :param damage: damage by which health is reduced
        """
        self._health -= damage
        # TODO: process player death.

    def _move(self, dt: float, keys: Sequence[bool]) -> None:
        direction = Vector2(0)

        if keys[pg.K_w]:
            direction += self.view_vector
        if keys[pg.K_s]:
            direction -= self.view_vector
        if keys[pg.K_COMMA]:
            direction += self.view_vector.rotate(-90)  # noqa: WPS432 -90deg
        if keys[pg.K_PERIOD]:
            direction += self.view_vector.rotate(90)  # noqa: WPS432 90deg

        # ??? Should we fix faster movement on diagonal?
        new = self._position + direction * dt * self.movement_speed
        old = self._position

        if self._map[int(old.y), int(new.x)] == 0:  # noqa: WPS221
            self._position.x = new.x
        if self._map[int(new.y), int(old.x)] == 0:  # noqa: WPS221
            self._position.y = new.y

    def _rotate(self, dt: float, keys: Sequence[bool]) -> None:
        if keys[pg.K_a]:
            self._angle -= self.rotation_speed * dt
        if keys[pg.K_d]:
            self._angle += self.rotation_speed * dt

    def _process_keys(self, dt: float) -> None:
        """Process pressed keys, move and rotate player.

        :param dt: delta time
        """
        # Execute, while key is pressed, not single pushed
        keys = pg.key.get_pressed()
        self._move(dt, keys)
        self._rotate(dt, keys)
        if keys[pg.K_SPACE]:
            self._shoot()

    def _shoot(self) -> None:
        print("SHOOT!")
