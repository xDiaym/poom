"""Base entity class."""
from abc import ABC, abstractmethod

import pygame as pg

from poom.viewer import Viewer


class Renderable(ABC):
    @property
    @abstractmethod
    def texture(self) -> pg.Surface:
        """Return current texture."""


# ??? Can be protocol?
class Damagable(ABC):
    """Interface for evrything, that has health."""

    @abstractmethod
    def take_damage(self, damage: float) -> None:
        """Decrease health.

        :param damage: damage by which health is reduced
        """

    @property
    @abstractmethod
    def hitbox_width(self) -> float:
        """Return hitbox width."""

    @abstractmethod
    def get_health(self) -> float:
        """Return current health."""

    @abstractmethod
    def get_health_ratio(self) -> float:
        """Return ration between current health and max health."""


class Entity(ABC, Viewer):
    """Base entity.

    Entity is an object, which has position, angle, FOV and texture.
    Entities support updating using :meth:`~Entity.update`.
    Entities can be rendered using :mod:`pooma`.
    """

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update entity state.

        :param dt: delta time
        """


class Pawn(Entity, Damagable, ABC):
    """Entity with health."""
