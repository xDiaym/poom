"""Describes player."""
from pathlib import Path
from typing import Callable, Collection, Final, Sequence

import numpy as np
import pygame as pg
from numpy.typing import NDArray
from pygame.math import Vector2

import poom.shared as shared
from poom.entities import Pawn, WithHealth
from poom.gun.player_gun import PlayerGun
from poom.settings import ROOT

OnDeathCallback = Callable[[], None]
settings = shared.Settings.load(ROOT)


class Player(Pawn, WithHealth):
    """Player."""

    max_health: Final[float] = 100
    movement_speed: Final[float] = 5
    rotation_speed: Final[float] = 3
    sound_path: Final[Path] = ROOT / "assets" / "sounds" / "player_injured.mp3"
    sound: Final[pg.mixer.Sound] = pg.mixer.Sound(sound_path)

    def __init__(
        self,
        *,
        map_: NDArray[np.int8],
        gun: PlayerGun,
        position: Vector2,
        angle: float,
        fov: float,
        enemies: Collection[Pawn],
    ) -> None:
        super().__init__(position, angle, fov)
        self._gun = gun
        self._map = map_
        self._health = self.max_health
        self._enemies = enemies
        self._on_death: OnDeathCallback = lambda: None
        self._channel = pg.mixer.Channel(1)
        self._channel.set_volume(settings.volume / 100)

    def on_death(self, cb: OnDeathCallback) -> None:
        """Set callback for death event."""
        self._on_death = cb

    @property
    def hitbox_width(self) -> float:
        """Return player hitbox width."""
        return 0.5

    def update(self, dt: float) -> None:
        """Update player state.

        :param dt: delta time
        """
        self._process_keys(dt)
        self._gun.update(dt)

    def take_damage(self, damage: float) -> None:
        """Decrease health.

        :param damage: damage by which health is reduced
        """
        self._channel.play(self.sound)
        self._health -= damage
        if self._health <= 0:
            self._on_death()

    def get_health(self) -> float:
        """Return current health."""
        return self._health

    def get_health_ratio(self) -> float:
        """Return ration between current health and max health."""
        return self._health / self.max_health

    def _move(self, dt: float, keys: Sequence[bool]) -> None:
        direction = Vector2(0)

        if keys[pg.K_w]:
            direction += self.view_vector
        if keys[pg.K_s]:
            direction -= self.view_vector
        if keys[pg.K_COMMA]:
            direction += self.view_vector.rotate(-90)  # noqa: WPS432 -90deg
        if keys[pg.K_PERIOD]:
            direction += self.view_vector.rotate(90)  # noqa: WPS432 90deg

        # ??? Should we fix faster movement on diagonal?
        new = self._position + direction * dt * self.movement_speed
        old = self._position

        if self._map[int(old.y), int(new.x)] == 0:  # noqa: WPS221
            self._position.x = new.x
        if self._map[int(new.y), int(old.x)] == 0:  # noqa: WPS221
            self._position.y = new.y

    def _rotate(self, dt: float, keys: Sequence[bool]) -> None:
        if keys[pg.K_a]:
            self._angle -= self.rotation_speed * dt
        if keys[pg.K_d]:
            self._angle += self.rotation_speed * dt

    def _process_keys(self, dt: float) -> None:
        """Process pressed keys, move and rotate player.

        :param dt: delta time
        """
        # Execute, while key is pressed, not single pushed
        keys = pg.key.get_pressed()
        self._move(dt, keys)
        self._rotate(dt, keys)
        self._shoot(keys)

    def _shoot(self, keys: Sequence[bool]) -> None:
        """Shoot, if space pressed.

        :param keys: array of keys
        """
        if keys[pg.K_SPACE]:
            self._gun.shoot(self._position, self._angle, self._enemies)
