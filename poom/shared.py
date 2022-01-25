import json
from abc import ABC, abstractmethod
from typing import Collection, List

import pygame as pg
from pygame.event import Event


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
