"""Base entity class."""
from abc import ABC, abstractmethod

import pygame as pg

from poom.viewer import Viewer


class Entity(ABC, Viewer):
    """Base entity.

    Entity is an object, which has position, angle, FOV and texture.
    Entities support updating using :meth:`~Entity.update`.
    Entities can be rendered using :mod:`pooma`.
    """

    @property
    @abstractmethod
    def texture(self) -> pg.Surface:
        """Return current texture."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update entity state.

        :param dt: delta time
        """
