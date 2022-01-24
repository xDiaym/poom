from abc import ABC, abstractmethod
from os import listdir
from pathlib import Path
from typing import List

import pygame as pg


class Animation:
    """Changes the animation frame depending on the time."""

    def __init__(self, images: List[pg.Surface], speed: float) -> None:
        self._images = images
        self._speed = speed
        self._animation_rate: float = 0

    def update(self, dt: float) -> None:
        self._animation_rate += dt * self._speed

    def flip_images(self) -> None:
        for index, image in enumerate(self._images):
            self._images[index] = pg.transform.flip(
                image,
                flip_x=True,
                flip_y=False,
            )

    def reset(self) -> None:
        self._animation_rate = 0

    @property
    def done(self) -> float:
        return self._animation_rate > len(self._images)

    @property
    def current_frame(self) -> pg.Surface:
        return self._images[int(self._animation_rate) % len(self._images)]

    @classmethod
    def from_dir(
        cls,
        root: Path,
        speed: float,
        scale: float = 1,
    ) -> "Animation":
        filenames = sorted(
            listdir(root),
            key=lambda filename: int(Path(filename).stem),
        )
        images = []
        for name in filenames:
            source = pg.image.load(root / name).convert_alpha()
            new_size = (
                int(source.get_width() * scale),
                int(source.get_height() * scale),
            )
            images.append(pg.transform.scale(source, new_size))

        return cls(images, speed)


class Animated(ABC):
    @property
    @abstractmethod
    def current_frame(self) -> pg.Surface:
        """Return current animation frame."""
