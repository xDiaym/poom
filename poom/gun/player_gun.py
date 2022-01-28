from pathlib import Path
from typing import Collection, Final

import pygame as pg
from poom.animated import Animation

from poom.entities import Pawn, Renderable
from poom.gun.gun import Gun
from poom.level import Map
from poom.settings import ROOT



class PlayerGun(Renderable):
    """Gun with texture and reload animation.

    Used as player gun.
    """

    sound_path: Final[Path] = ROOT / "assets" / "sounds" / "player_ssg.mp3"
    sound: Final[pg.mixer.Sound] = pg.mixer.Sound(sound_path)

    def __init__(self, gun: Gun, animation: Animation) -> None:
        """Initialize animated gun.

        :param gun: gun instance
        :param animation: gun animation
        """
        self._gun = gun
        self._animation = animation
        self.channel = pg.mixer.Channel(2)

    def shoot(
        self,
        position: pg.Vector2,
        angle: float,
        enemies: Collection["Pawn"],
    ) -> None:
        """Shoot to enemies.

        :param position: shooter position
        :param angle: shooter angle
        :param enemies: enemies
        """
        if not self.channel.get_busy():
            self.channel.play(self.sound)
        self._gun.shoot(position, angle, enemies)

    @property
    def texture(self) -> pg.Surface:
        """Return gun texture."""
        return self._animation.current_frame

    def update(self, dt: float) -> None:
        """Update gun texture.

        :param dt: delta time
        """
        self._gun.update(dt)
        if self._gun.reloading:
            self._animation.update(dt)
        else:
            self._animation.reset()


def create_player_gun(
    level_map: Map,
    reload_time: float,
    damage: float,
    animation_path: Path,
    scale: float,
) -> PlayerGun:
    gun = Gun(level_map, reload_time, damage)
    animation = Animation.from_dir(animation_path, reload_time, scale)
    return PlayerGun(gun, animation)
