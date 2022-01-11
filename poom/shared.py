from abc import ABC, abstractmethod
import pygame as pg
import pygame_gui
from pathlib import Path


class ScreenResizer:
    def __init__(self, width: int, height: int, root: Path) -> None:
        self.resize(width, height, root)

    def resize(self, width, height, root) -> None:
        self.size = self.width, self.height = width, height
        self.surface = pg.display.set_mode(self.size)
        self.background = pg.transform.scale(
            pg.image.load(root / "assets" / "back.png").convert_alpha(), (width, height)
        )
        self.manager = pygame_gui.UIManager(self.size, root / "assets" / "style.json")


class AbstractScene(ABC):
    def __init__(self, context: "SceneContext") -> None:
        self._context = context

    @abstractmethod
    def on_click(self, event) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, render: pg.Surface) -> None:
        pass


class SceneContext:
    def __init__(self, first_scene) -> None:
        self._scene = first_scene(self)

    @property
    def scene(self) -> AbstractScene:
        return self._scene

    @scene.setter
    def scene(self, value: AbstractScene) -> None:
        self._scene = value

    def handler(self, event) -> None:
        self._scene.on_click(event)

    def render(self, screen: ScreenResizer, clock: pg.time.Clock) -> None:
        screen.surface.blit(screen.background, (0, 0))
        self._scene.render(screen.surface)
        self._scene.update(clock.tick() / 1000)
