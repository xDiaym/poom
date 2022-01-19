"""Describes player."""
from typing import Final

import pygame as pg
from pygame.event import Event
from pygame.math import Vector2

from poom.entities.damagable import Damagable
from poom.viewer import Viewer


class Player(Damagable, Viewer):
    """Player."""

    max_health: Final[float] = 100
    movement_speed: Final[float] = 5
    rotation_speed: Final[float] = 0.3

    def __init__(self, *, position: Vector2, angle: float, fov: float) -> None:
        super().__init__(position, angle, fov)
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

    def _process_keys(self, dt: float) -> None:
        """Process pressed keys and move player.

        :param dt: delta time
        """
        # Execute, while key is pressed, not single pushed
        keys = pg.key.get_pressed()
        direction = Vector2(0)
        if keys[pg.K_w]:
            direction += self.view_vector
        if keys[pg.K_s]:
            direction -= self.view_vector
        if keys[pg.K_a]:
            direction += self.view_vector.rotate(-90)  # noqa: WPS432: -90 deg
        if keys[pg.K_d]:
            direction += self.view_vector.rotate(90)  # noqa: WPS432: 90 deg
        self._position += direction * dt * self.movement_speed

    def _process_mouse(self, dt: float) -> None:
        """Update player angle.

        :param dt: delta time
        """
        # FIXME: has side effects. Move to game class
        x_movement, _ = pg.mouse.get_rel()
        self._angle += x_movement * self.rotation_speed * dt
