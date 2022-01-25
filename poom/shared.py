import json
from abc import ABC, abstractmethod
from os import listdir
from pathlib import Path
from typing import Collection, List

import pygame as pg
import pygame_gui
from pygame.event import Event


class Animation:
    def __init__(self, images: list, speed: float) -> None:
        self._images = images
        self._speed = speed
        self._animation_rate = 0

    def update(self, dt: float) -> None:
        self._animation_rate += dt * self._speed

    def flip_images(self) -> None:
        for i in range(len(self._images)):
            self._images[i] = pg.transform.flip(self._images[i], True, False)

    def reset(self) -> None:
        self._animation_rate = 0

    @property
    def done(self) -> float:
        return self._animation_rate > len(self._images)

    @property
    def current_frame(self) -> pg.Surface:
        return self._images[int(self._animation_rate) % len(self._images)]

    @classmethod
    def from_dir(cls, root: Path, speed: float, scale: float = 1):
        filenames = sorted(listdir(root), key=lambda x: int(Path(x).stem))
        images = []
        for name in filenames:
            path = root / name
            source = pg.image.load(path).convert_alpha()
            images.append(
                pg.transform.scale(
                    source,
                    (
                        int(source.get_width() * scale),
                        int(source.get_height() * scale),
                    ),
                )
            )
        return cls(images, speed)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# TODO: move to file
class Settings(dict, metaclass=Singleton):
    def __init__(self, root):
        with open(root / "assets" / "settings.json") as file:
            data = json.load(file)
        for key in data:
            setattr(self, key, data[key])

    def update(self, root):
        with open(root / "assets" / "settings.json", "w") as file:
            json.dump(vars(self), file)


class AbstractScene(ABC):
    def __init__(self, context: "SceneContext") -> None:
        self._context = context

    @abstractmethod
    def on_event(self, event: Collection[Event]) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, render: pg.Surface) -> None:
        pass


class SceneContext:
    def __init__(self, first_scene: AbstractScene, screen: pg.Surface) -> None:
        self.screen = screen
        self._scene = first_scene(self)

    @property
    def scene(self) -> AbstractScene:
        return self._scene

    @scene.setter
    def scene(self, value: AbstractScene) -> None:
        self._scene = value

    def on_event(self, events: List[Event]) -> None:
        self._scene.on_event(events)

    def render(self) -> None:
        self._scene.render()

    def update(self, dt):
        self._scene.update(dt)
