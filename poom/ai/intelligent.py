from abc import ABC, abstractmethod
from typing import List, Tuple

import pygame as pg

from poom.animated import Animation
from poom.entities import Pawn
from poom.level import Map

Point = pg.Vector2
Path = List[Point]


class AbstractIntelligent(Pawn, ABC):
    """Interface for entities controlled by artificial intelligence."""

    @abstractmethod
    def move_to(self, path: pg.Vector2) -> None:
        """Move along the specified path."""

    @abstractmethod
    def shoot(self) -> None:
        """Shoot on current direction from current position."""

    @abstractmethod
    def rotate_to(self, angle: float) -> None:
        """Set angle to specified angle."""

    @abstractmethod
    def die(self) -> None:
        """Kill itself."""

    @abstractmethod
    def set_animation(self, animation: Animation) -> None:
        """Set animation to specified one."""

    @abstractmethod
    def can_cause_damage(self) -> bool:
        """Return true if can cause damage to enemy, otherwise false"""

    @property
    @abstractmethod
    def animation_done(self) -> bool:
        """Return true if animation is done."""

    @property
    @abstractmethod
    def enemy(self) -> Pawn:
        """Return owner enemy."""

    @property
    @abstractmethod
    def wall_nearby(self) -> bool:
        """Checks if npc is in contact with the wall."""

    @property
    @abstractmethod
    def map_(self) -> Map:
        """Return level map."""
