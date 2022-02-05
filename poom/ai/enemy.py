from math import atan2
from random import random
from typing import Any, Final, List

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.ai.decision import make_decision
from poom.ai.intelligent import AbstractIntelligent
from poom.animated import Animation
from poom.entities import Entity, Pawn, Renderable
from poom.gun.gun import Gun
from poom.level import Map, map2d
from poom.settings import ROOT
from poom.shared import Settings
from poom.viewer import Viewer

settings = Settings.load(ROOT)


class Enemy(AbstractIntelligent, Pawn, Renderable):
    """Enemy is an aggressive to player entity."""

    max_health: Final[float] = 15
    if settings.difficulty == "Low":
        hit_chance: float = 0.1
    elif settings.difficulty == "Medium":
        hit_chance: float = 0.3
    else:
        hit_chance: float = 0.5

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
        self.ai_map = map2d(map_, lambda x: 1 if x == 0 else 0)
        self._ai_enemy = ai_enemy
        self._texture = texture
        self._health = self.max_health
        self._gun = Gun(map_, 1, 20)
        self._enemies = entities
        self._action = make_decision(self)
        self._action.apply()

    def move_to(self, point: pg.Vector2) -> None:
        self._position = point

    def shoot(self) -> None:
        if random() < self.hit_chance:
            self._gun.shoot(self.position, self.angle, [self._ai_enemy])

    def rotate_to(self, angle: float) -> None:
        self._angle = angle

    def die(self) -> None:
        self._enemies.remove(self)

    def set_animation(self, animation: Animation) -> None:
        self._animation = animation

    def can_cause_damage(self) -> bool:
        return self._gun.can_cause_damage(self.position, self._angle, self._ai_enemy)

    @property
    def animation_done(self) -> bool:
        return self._animation.done

    @property
    def enemy(self) -> Pawn:
        return self._ai_enemy

    @property
    def wall_nearby(self) -> bool:
        direction = self._ai_enemy.position - self.position
        sign_x = 1 if direction.x > 0 else -1
        sign_y = 1 if direction.y > 0 else -1
        next_x, next_y = (
            self.position.x + 0.5 * sign_x,
            self.position.y + 0.5 * sign_y,
        )
        if (
            not self.ai_map[int(next_y)][int(self.position.x)]
            or not self.ai_map[int(self.position.y)][int(next_x)]
        ):
            return True
        return False

    @property
    def map_(self) -> Map:
        return self.ai_map

    def take_damage(self, damage: float) -> None:
        self._health -= damage
        if self._health <= 0:
            self._action = make_decision(self)
            self._action.apply()

    def get_health(self) -> float:
        return self._health

    def get_health_ratio(self) -> float:
        return self._health / self.max_health

    @property
    def texture(self) -> pg.Surface:
        return self._animation.current_frame

    @property
    def hitbox_width(self) -> float:
        return 0.25

    def update(self, dt: float) -> None:
        self._animation.update(dt)
        self._gun.update(dt)
        self._action.update(dt)

        if self._action.done:
            self._action = make_decision(self)
            self._action.apply()
