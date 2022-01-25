from abc import ABC, abstractmethod
from os import listdir
from pathlib import Path

import pygame as pg
import pygame_gui


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


class ScreenResizer:
    def __init__(self, width: int, height: int, root: Path) -> None:
        self.resize(width, height, root)

    def resize(self, width, height, root) -> None:
        self.size = self.width, self.height = width, height
        self.surface = pg.display.set_mode(self.size)
        self.background = pg.transform.scale(
            pg.image.load(root / "assets" / "back.png").convert_alpha(),
            (width, height),
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
