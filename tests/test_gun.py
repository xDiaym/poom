import numpy as np
import pygame as pg
import pytest
from poom.entities import Pawn

from poom.gun.gun import Gun
from poom.level import Map


@pytest.fixture
def clear_map() -> Map:
    return np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ], dtype=np.int8)


@pytest.fixture
def wall_map() -> Map:
    return np.array([
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
    ], dtype=np.int8)


class MockedPawn(Pawn):
    def __init__(self, position: pg.Vector2, angle: float, fov: float) -> None:
        super().__init__(position, angle, fov)
        self.taken_damage = 0

    def take_damage(self, damage: float) -> None:
        self.taken_damage += damage

    @property
    def hitbox_width(self) -> float:
        return 0.5

    def update(self, dt: float) -> None:
        """Do nothing."""


def test_can_shoot_on_clear_map(clear_map: Map) -> None:
    gun = Gun(clear_map, 0, 100)
    enemy = MockedPawn(pg.Vector2(2, 1), 0, 0)
    assert gun.can_cause_damage(pg.Vector2(1, 1), 0, enemy)


def test_can_shoot_on_wall_map(wall_map: Map) -> None:
    gun = Gun(wall_map, 0, 100)
    enemy = MockedPawn(pg.Vector2(3, 1), 0, 0)
    assert not gun.can_cause_damage(pg.Vector2(1, 1), 0, enemy)


def test_can_shoot_near_wall(wall_map: Map) -> None:
    gun = Gun(wall_map, 0, 100)
    enemy = MockedPawn(pg.Vector2(1, 2.5), 0, 0)
    assert not gun.can_cause_damage(pg.Vector2(1, 2), 0, enemy)
