"""Base entity class."""
import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.map_loader import map2d
from poom.npc import EnemyIntelligence
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

    def __init__(
        self,
        texture: pg.Surface,
        enemy: Viewer,
        map_: NDArray[np.uint8],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        map_ = map2d(map_, lambda x: 1 if x == 0 else 0)
        self._intelligence = EnemyIntelligence(self, enemy, map_)
        self._texture = texture

    @property
    def texture(self) -> pg.Surface:
        return self._texture

    def update(self, dt: float) -> None:
        self._intelligence.update(dt)

    def take_damage(self, damage: float) -> None:
        logging.debug("ouch. that hurts. %f", damage)

    @property
    def hitbox_width(self) -> float:
        return 0.25
