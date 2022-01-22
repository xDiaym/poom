"""Enemy class."""
from typing import Any

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.entities.entity import Entity
from poom.map_loader import map2d
from poom.npc import EnemyIntelligence
from poom.viewer import Viewer


class Enemy(Entity):
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
