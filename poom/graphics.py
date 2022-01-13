""" All utils for graphics pipeline. """
import os
import typing
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
import pygame as pg

from numpy.typing import NDArray
from poom.map_loader import Map
from poom.pooma.ray_march import draw_walls  # pylint: disable=E0611
from poom.viewer import Viewer


StencilBuffer: typing.TypeAlias = NDArray[np.float]


class AbstractRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def __call__(self, surface: pg.Surface, stencil: StencilBuffer) -> None:
        """ Method for rendering.

        :param surface: surface for rendering
        :param stencil: stencil buffer
        """


class FPSRenderer(AbstractRenderer):
    """Displays colorized fps counter."""

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

    def __call__(self, surface: pg.Surface, _: StencilBuffer) -> None:
        fps, color = self._clock.get_fps(), "red"
        if fps >= 30:
            color = "yellow"
        if fps >= 60:
            color = "green"

        fps_image = self._font.render(f"{fps:.0f}", True, color)
        surface.blit(fps_image, self._position)


class WallRenderer(AbstractRenderer):
    """ Render walls using ray marching(DDA) algorithm. """

    def __init__(self, map_: Map, viewer: Viewer) -> None:
        self._map = map_
        self._viewer = viewer  # ??? maybe use RenderContext?

        # Use image loader instead of this garbage
        path1 = os.path.abspath("./assets/textures/1.png")
        path2 = os.path.abspath("./assets/textures/2.png")
        self._textures = [pg.image.load(path1), pg.image.load(path2)]

    def __call__(self, surface: pg.Surface, stencil: StencilBuffer) -> None:
        draw_walls(
            self._map,
            surface,
            stencil,
            self._textures,
            *self._viewer.position,
            self._viewer.angle,
            self._viewer.fov,
        )


class Pipeline:
    """Manipulate with renderers."""

    def __init__(self, renderers: List[AbstractRenderer]) -> None:
        self._renderers = renderers

    def render(self, surface: pg.Surface) -> None:
        """Calls all renderers in the order in which they were passed
        to :func:`~Pipeline.__init__`

        :param surface: surface for rendering
        """
        stencil = np.full(surface.get_width(), np.inf, dtype=np.float32)
        surface.fill("black")
        for renderer in self._renderers:
            renderer(surface, stencil)
        pg.display.flip()
