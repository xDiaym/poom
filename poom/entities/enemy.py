"""Enemy class."""
from typing import Any

import pygame as pg

from poom.entities.entity import Entity


class Enemy(Entity):
    """Enemy is an aggressive to player entity."""

    def __init__(self, texture: pg.Surface, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._texture = texture

    @property
    def texture(self) -> pg.Surface:
        return self._texture

    def update(self, dt: float) -> None:
        pass
