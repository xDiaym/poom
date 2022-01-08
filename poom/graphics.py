import os
from abc import ABC, abstractmethod
from math import cos
from typing import List, Optional

import pygame as pg

from poom.map_loader import Map
from poom.ray_march import draw_walls
from poom.viewer import Viewer


class AbstractRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def __call__(self, surface: pg.Surface) -> None:
        """Method for rendering."""


class FPSRenderer(AbstractRenderer):
    def __init__(
        self,
        clock: pg.time.Clock,
        font_name: Optional[str] = None,
        font_size: int = 32,
        position: pg.Vector2 = None,
    ) -> None:
        self._clock = clock
        self._font = pg.font.Font(font_name, font_size)
        self._position = position or pg.Vector2(0.0, 0.0)

    def __call__(self, surface: pg.Surface) -> None:
        fps, color = self._clock.get_fps(), "red"
        if fps >= 30:
            color = "yellow"
        if fps >= 60:
            color = "green"

        fps_image = self._font.render("%2.f" % fps, True, color)
        surface.blit(fps_image, self._position)


class WallRenderer(AbstractRenderer):
    def __init__(self, map_: Map, viewer: Viewer) -> None:
        self._map = map_
        self._viewer = viewer  # ??? maybe use RenderContext?
        path = os.path.abspath("./assets/textures/wall.png")
        self._texture = pg.image.load(path)

    # TODO(optimization): rewrite it in Cython
    def __call__(self, surface: pg.Surface) -> None:
        x, y = self._viewer.position
        angle = self._viewer.angle
        fov = self._viewer.fov
        draw_walls(self._map, surface, self._texture, x, y, angle, fov)


class Pipeline:
    def __init__(self, renderers: List[AbstractRenderer]) -> None:
        self._renderers = renderers

    def render(self, surface: pg.Surface) -> None:
        surface.fill("black")
        for renderer in self._renderers:
            renderer(surface)
        pg.display.flip()
