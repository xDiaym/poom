from abc import ABC, abstractmethod
from math import atan2
from pathlib import Path
from random import random
from typing import Any, Final, List, Tuple

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pathfinding.core.grid import Grid
from pathfinding.finder.best_first import BestFirst

import poom.shared as shared
from poom.animated import Animation
from poom.entities import Entity, Pawn, Renderable
from poom.gun.gun import Gun
from poom.level import map2d
from poom.settings import ROOT
from poom.viewer import Viewer

Coords = Tuple[int, int]
settings = shared.Settings.load(ROOT)


class Enemy(Pawn, Renderable):
    """Enemy is an aggressive to player entity."""

    max_health: Final[float] = 15
    sound_path: Final[Path] = ROOT / "assets" / "sounds" / "bot_injured.mp3"
    sound: Final[pg.mixer.Sound] = pg.mixer.Sound(sound_path)

    def __init__(
        self,
        texture: pg.Surface,
        ai_enemy: Viewer,
        entities: List[Entity],
        map_: NDArray[np.uint8],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        ai_map = map2d(map_, lambda x: 1 if x == 0 else 0)
        self._ai_enemy = ai_enemy
        self._intelligence = EnemyIntelligence(self, ai_enemy, ai_map)
        self._texture = texture
        self._health = self.max_health
        self._gun = Gun(map_, 1, 100)
        self._enemies = entities
        self.channel = pg.mixer.Channel(3)
        self.channel.set_volume(settings.volume / 100)

    @property
    def texture(self) -> pg.Surface:
        return self._texture

    def update(self, dt: float) -> None:
        self._intelligence.update(dt)
        self._gun.update(dt)

    def can_cause_damage(self) -> bool:
        return self._gun.can_cause_damage(self.position, self.angle, self._ai_enemy)

    def take_damage(self, damage: float) -> None:
        self._health -= damage
        if self._health <= 0 and not isinstance(self._intelligence.state, Die):
            self._intelligence.state = Die(self._intelligence)
        else:
            self.channel.play(self.sound)

    def die(self) -> None:
        self._enemies.remove(self)

    @property
    def hitbox_width(self) -> float:
        return 0.25


class EnemyIntelligence:
    def __init__(self, owner: Enemy, enemy: Viewer, map_: NDArray[np.int8]) -> None:
        self._owner = owner
        self._enemy = enemy
        self._map = map_
        self._state = Chase(self, self._enemy, map_)

    @property
    def owner(self) -> Enemy:
        return self._owner

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: "AbstractAIState") -> None:
        self._state = state

    def update(self, dt: float) -> None:
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
    max_distance: Final[float] = 1.5
    best_first: Final[int] = 1
    vector_form: Final[int] = 0

    def __init__(
        self,
        context: EnemyIntelligence,
        enemy: Viewer,
        map_: NDArray[np.uint8],
    ) -> None:
        super().__init__(context)
        self._animation = Animation.from_dir(
            ROOT / "assets" / "sprites" / "front_walk", 1, 1
        )

        self._enemy = enemy
        self._algo = self._is_wall
        if self._algo == self.best_first:
            self._grid = Grid(matrix=map_)
            self._finder = BestFirst()
            start = list(map(int, context.owner.position))
            end = list(map(int, enemy.position))
            self._path = self._find_path(start, end)[1 : self.max_steps + 1]
            self._current_point_index = 0
        else:
            self.stop = enemy.position - context.owner.position
            self.stop.scale_to_length(2)
            self.stop += context.owner.position

    def _find_path(self, start: Coords, dest: Coords) -> List[Coords]:
        point1 = self._grid.node(*start)
        point2 = self._grid.node(*dest)
        path, _ = self._finder.find_path(point1, point2, self._grid)
        return path

    @property
    def current_point(self) -> pg.Vector2:
        if len(self._path) == 0:
            return self._context.owner.position
        point = pg.Vector2(*self._path[self._current_point_index])
        return point + pg.Vector2(0.5)

    @property
    def _is_wall(self) -> bool:
        owner = self._context.owner
        direction = self._enemy.position - owner.position
        sign_x = 1 if direction.x > 0 else -1
        sign_y = 1 if direction.y > 0 else -1
        next_x, next_y = (
            owner.position.x + 0.5 * sign_x,
            owner.position.y + 0.5 * sign_y,
        )
        if (
            not self._context._map[int(next_y)][int(owner.position.x)]
            or not self._context._map[int(owner.position.y)][int(next_x)]
        ):
            return True
        return False

    def update(self, dt: float) -> None:
        owner = self._context.owner
        if self._algo == self.vector_form and self._is_wall:
            self._context.state = Chase(self._context, self._enemy, self._context._map)
            return
        if self._algo == self.best_first:
            self.direction = self.current_point - owner.position
        else:
            self.direction = self.stop - owner.position
        target_distance = (owner.position - self._enemy.position).magnitude()

        if target_distance < self.max_distance:
            self._context.state = Attack(self._context)
            return

        owner._position += self.direction.normalize() * self.chasing_speed * dt
        if self.direction.magnitude() < self.epsilon:
            if self._algo == self.best_first:
                if self._current_point_index == len(self._path) - 1:
                    self._context.state = Attack(self._context)
                else:
                    self._current_point_index += 1
            else:
                self._context.state = Attack(self._context)
        self._animation.update(dt)
        # ohh
        self._context.owner._texture = self._animation.current_frame


class Attack(AbstractAIState):
    if settings.difficulty == "Low":
        hit_chance: float = 0.1
    elif settings.difficulty == "Medium":
        hit_chance: float = 0.3
    else:
        hit_chance: float = 0.5
    sound_path: Final[Path] = ROOT / "assets" / "sounds" / "bot_fire.mp3"
    sound: Final[pg.mixer.Sound] = pg.mixer.Sound(sound_path)

    def __init__(self, context: EnemyIntelligence) -> None:
        super().__init__(context)
        self._animation = Animation.from_dir(
            ROOT / "assets" / "sprites" / "front_attack", 0.7, 1
        )
        self._rotate_to_enemy()
        owner = context.owner
        if owner.can_cause_damage():
            self._shoot()
        else:
            context.state = Chase(
                self._context,
                self._context._enemy,
                self._context._map,
            )

    def update(self, dt: float) -> None:
        self._animation.update(dt)
        self._context.owner._texture = self._animation.current_frame
        if self._animation.done:
            state = Chase(
                self._context,
                self._context._enemy,
                self._context._map,
            )
            self._context.state = state

    def _rotate_to_enemy(self) -> None:
        owner = self._context.owner
        direction = (owner.position - self._context._enemy.position)
        owner._angle = atan2(direction.y, direction.x)

    def _shoot(self) -> None:
        channel = pg.mixer.Channel(0)
        channel.set_volume(1)
        channel.play(self.sound)
        
        owner = self._context.owner
        if random() < self.hit_chance:
            owner._gun.shoot(owner.position, owner.angle, [self._context._enemy])


class Die(AbstractAIState):
    sound_path: Final[Path] = ROOT / "assets" / "sounds" / "bot_death.mp3"
    sound: Final[pg.mixer.Sound] = pg.mixer.Sound(sound_path)

    def __init__(self, context: EnemyIntelligence) -> None:
        super().__init__(context)
        self._animation = Animation.from_dir(ROOT / "assets" / "sprites" / "die", 2, 1)
        channel = pg.mixer.Channel(0)
        channel.set_volume(settings.volume / 100)
        channel.play(self.sound)

    def update(self, dt: float) -> None:
        self._animation.update(dt)
        self._context.owner._texture = self._animation.current_frame
        if self._animation.done:
            self._context.owner.die()
