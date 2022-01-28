import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Collection, List, Optional

if TYPE_CHECKING:
    from poom.game import Game

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
@dataclass
class Settings(metaclass=Singleton):
    difficulty: float
    screen_size: List[int]
    ratio: str
    volume: int
    fps_tick: int

    @staticmethod
    def load(root: Path):
        with open(root / "assets" / "settings.json") as file:
            data = json.load(file)
        return Settings(
            data["difficulty"],
            data["screen_size"],
            data["ratio"],
            data["volume"],
            data["fps_tick"],
        )

    def update(self, root: Path):
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
    def render(self) -> None:
        pass


class SceneContext:
    def __init__(self, screen: pg.Surface, game: "Game") -> None:
        self._screen = screen
        self._game = game
        self._scene: Optional[AbstractScene] = None

    @property
    def screen(self) -> pg.Surface:
        return self._screen

    @property
    def game(self) -> "Game":
        return self._game

    @property
    def scene(self) -> AbstractScene:
        assert self._scene, "Scene can't be None."
        return self._scene

    @scene.setter
    def scene(self, scene: AbstractScene) -> None:
        self._scene = scene

    def on_event(self, events: List[Event]) -> None:
        self._scene.on_event(events)

    def render(self) -> None:
        self._scene.render()

    def update(self, dt):
        self._scene.update(dt)
