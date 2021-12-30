from abc import ABC, abstractmethod
from math import cos
from typing import List, Optional

import pygame as pg

from poom.map_loader import Map
from poom.ray_march import ray_march
from poom.viewer import Viewer


class AbstractRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def __call__(self, surface: pg.Surface) -> None:
        """Method for redering."""


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

    # TODO(optimization): rewrite it in Cython
    def __call__(self, surface: pg.Surface) -> None:
        width, height = surface.get_size()
        for x in range(width):
            alpha = x / width * self._viewer.fov
            angle = self._viewer.angle - self._viewer.fov / 2 + alpha
            x0, y0 = self._viewer.position
            dist = ray_march(self._map, x0, y0, angle)
            half_height = (
                int(height / (dist * cos(angle - self._viewer.angle))) // 2
            )  # TODO: fix parabola-like walls
            pg.draw.line(
                surface,
                "white",
                (x, height // 2 - half_height),
                (x, height // 2 + half_height),
            )


class Pipeline:
    def __init__(self, renderers: List[AbstractRenderer]) -> None:
        self._renderers = renderers

    def render(self, surface: pg.Surface) -> None:
        surface.fill("black")
        for renderer in self._renderers:
            renderer(surface)
        pg.display.flip()
