from abc import ABC, abstractmethod
from math import atan2
from typing import Final, Optional

import pygame as pg
from pathfinding.core.grid import Grid
from pathfinding.finder.best_first import BestFirst

from poom.ai.intelligent import AbstractIntelligent, Path, Point
from poom.resources import R
from poom.settings import ROOT
from poom.shared import Settings

settings = Settings.load(ROOT)


class AbstractAction(ABC):
    @abstractmethod
    def apply(self) -> None:
        """Initialize settings."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Apply action to owner."""

    @property
    @abstractmethod
    def done(self) -> bool:
        """Return true if action is done, otherwise false."""


class AttackAction(AbstractAction):
    def __init__(
        self,
        owner: AbstractIntelligent,
        enemy_position: pg.Vector2,
    ) -> None:
        self._owner = owner
        self._enemy_position = enemy_position
        self._channel = pg.mixer.Channel(1)
        self._channel.set_volume(settings.volume / 100)

    def apply(self) -> None:
        self._owner.set_animation(R.animation.get("front_attack", 3, 1))

        direction = self._enemy_position - self._owner.position
        angle = atan2(direction.y, direction.x)

        self._owner.rotate_to(angle)
        self._owner.shoot()

        sound = R.sound.get("bot_fire.mp3")
        self._channel.play(sound)

    def update(self, dt: float) -> None:
        """Do nothing"""

    @property
    def done(self) -> bool:
        return self._owner.animation_done


class DieAction(AbstractAction):
    def __init__(self, owner: AbstractIntelligent) -> None:
        self._owner = owner
        self._channel = pg.mixer.Channel(4)
        self._channel.set_volume(settings.volume / 100)

    def apply(self) -> None:
        self._owner.set_animation(R.animation.get("die", 5, 1))

        sound = R.sound.get("bot_death.mp3")
        self._channel.play(sound)

    def update(self, dt: float) -> None:
        if self._owner.animation_done:
            self._owner.die()

    @property
    def done(self) -> None:
        return self._owner.animation_done


class DiagonalChaseAction(AbstractAction):
    epsilon: Final[float] = 1e-1
    minimal_distance: Final[float] = 1.5
    chase_speed: Final[float] = 0.35

    def __init__(self, owner: AbstractIntelligent) -> None:
        self._owner = owner

    def apply(self) -> None:
        animation = R.animation.get("front_walk", 5, 1)
        self._owner.set_animation(animation)

        self.path = self._owner.enemy.position - self._owner.position
        self.path.scale_to_length(2)
        self.dest = self.path + self._owner.position

    def update(self, dt: float) -> None:
        point = self._owner.position + self.path * self.chase_speed * dt
        self._owner.move_to(point)

    @property
    def done(self) -> bool:
        end = self.dest - self._owner.position
        return (
            end.magnitude() < self.epsilon
            or self._owner.wall_nearby
            or self._owner.player_nearby
        )


class AStarChaseAction(AbstractAction):
    epsilon: Final[float] = 1e-1
    minimal_distance: Final[float] = 1.5
    chase_speed: Final[float] = 0.5

    def __init__(self, owner: AbstractIntelligent) -> None:
        self._owner = owner
        self._path: Optional[Path] = None
        self._point_index = 0

    def apply(self) -> None:
        animation = R.animation.get("front_walk", 5, 1)
        self._owner.set_animation(animation)
        self._path = self._find_path()

    def update(self, dt: float) -> None:
        end = self.current_point - self._owner.position
        point = self._owner.position + end.normalize() * self.chase_speed * dt
        self._owner.move_to(point)

        if end.magnitude() < self.epsilon:
            self._point_index += 1

    @property
    def done(self) -> bool:
        return self._point_index >= len(self._path) or self._owner.player_nearby

    @property
    def current_point(self) -> Point:
        if len(self._path) == 0:
            return self._owner.position
        return pg.Vector2(*self._path[self._point_index]) + pg.Vector2(0.5)

    def _find_path(self) -> Path:
        grid = Grid(matrix=self._owner.map_)
        finder = BestFirst()
        start = list(map(int, self._owner.position))
        end = list(map(int, self._owner.enemy.position))
        point1 = grid.node(*start)
        point2 = grid.node(*end)
        path, _ = finder.find_path(point1, point2, grid)
        return path[1:3]
