"""Base entity class."""
from abc import ABC, abstractmethod
from typing import Any

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


class Enemy(Pawn, Renderable):
    """Enemy is an aggressive to player entity."""

    def __init__(self, texture: pg.Surface, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._texture = texture

    def update(self, dt: float) -> None:
        pass

    def take_damage(self, damage: float) -> None:
        print(damage)

    @property
    def texture(self) -> pg.Surface:
        return self._texture

    @property
    def hitbox_width(self) -> float:
        return 0.25
