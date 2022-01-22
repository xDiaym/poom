from abc import ABC, abstractmethod
from os import getcwd
from pathlib import Path
from typing import Final, List, Tuple

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pathfinding.core.grid import Grid
from pathfinding.finder.best_first import BestFirst

from poom.shared import Animation
from poom.viewer import Viewer

root = Path(getcwd())

Coords = Tuple[int, int]


class EnemyIntelligence:
    def __init__(self, owner: Viewer, enemy: Viewer, map_: NDArray[np.int8]) -> None:
        self._prev_state = None
        self._owner = owner
        self._enemy = enemy
        self._map = map_
        self._state = Chase(self, self._enemy, map_)

    @property
    def owner(self) -> Viewer:
        return self._owner

    def set_state(self, state: "AbstractAIState") -> None:
        self._prev_state, self._state = self._state, state

    def update(self, dt: float) -> float:
        self._state.update(dt)


class AbstractAIState(ABC):
    def __init__(self, context: EnemyIntelligence) -> None:
        self._context = context

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update bot state

        :param dt: delta time
        """


class Chase(AbstractAIState):
    epsilon: Final[float] = 1e-2
    chasing_speed: Final[float] = 0.6
    max_steps: Final[int] = 2
    max_distance: Final[int] = 1.5

    def __init__(
        self,
        context: EnemyIntelligence,
        enemy: Viewer,
        map_: NDArray[np.uint8],
    ) -> None:
        super().__init__(context)
        self.walking_animation = Animation.from_dir(
            root / "assets" / "front_walk", 3, 1
        )

        self._enemy = enemy
        self._grid = Grid(matrix=map_)
        self._finder = BestFirst()
        start = list(map(int, context.owner.position))
        end = list(map(int, enemy.position))
        self._path = self._find_path(start, end)[1 : self.max_steps + 1]
        self._current_point_index = 0

    def _find_path(self, start: Coords, dest: Coords) -> List[Coords]:
        point1 = self._grid.node(*start)
        point2 = self._grid.node(*dest)
        path, _ = self._finder.find_path(point1, point2, self._grid)
        return path

    @property
    def current_point(self) -> pg.Vector2:
        point = pg.Vector2(*self._path[self._current_point_index])
        return point + pg.Vector2(0.5)

    def update(self, dt: float) -> None:
        owner = self._context.owner
        direction = self.current_point - owner.position
        target_distance = (owner.position - self._enemy.position).magnitude()

        if target_distance < self.max_distance:
            self._context.set_state(Attack(self._context))
            return

        owner._position += direction.normalize() * self.chasing_speed * dt
        if direction.magnitude() < self.epsilon:
            if self._current_point_index == len(self._path) - 1:
                state = Attack(self._context)
                self._context.set_state(state)
            else:
                self._current_point_index += 1
        self.walking_animation.update(dt)
        # ohh
        self._context.owner._texture = self.walking_animation.current_frame


class Attack(AbstractAIState):
    def __init__(self, context: EnemyIntelligence) -> None:
        super().__init__(context)
        self.fire_animation = Animation.from_dir(root / "assets" / "front_attack", 3, 1)
        pg.mixer.init()
        pg.mixer.music.load(root / "assets" / "dsshotgn.wav")
        pg.mixer.music.set_volume(0.2)
        pg.mixer.music.play(1)

    def update(self, dt: float) -> None:
        self.fire_animation.update(dt)
        self._context.owner._texture = self.fire_animation.current_frame
        if self.fire_animation.done:
            state = Chase(
                self._context,
                self._context._enemy,
                self._context._map,
            )
            self._context.set_state(state)
