"""All utils for graphics pipeline."""
import os
from abc import ABC, abstractmethod
from typing import Collection, Final, Optional

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.map_loader import Map
from poom.pooma.ray_march import draw_sprite, draw_walls  # pylint: disable=E0611
from poom.viewer import Viewer

StencilBuffer = NDArray[np.float32]


class AbstractRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def __call__(
        self,
        surface: pg.Surface,
        stencil: StencilBuffer,
        viewer: Viewer,
    ) -> None:
        """Render something into surface.

        :param surface: surface for rendering
        :param stencil: stencil buffer
        :param viewer: camera-like object
        """


class FPSRenderer(AbstractRenderer):
    """Displays colorized fps counter."""

    YELLOW_LIMIT: Final[int] = 30
    GREEN_LIMIT: Final[int] = 60

    def __init__(
        self,
        clock: pg.time.Clock,
        font_name: Optional[str] = None,
        font_size: int = 32,
        position: pg.Vector2 = None,
    ) -> None:
        self._clock = clock
        self._font = pg.font.Font(font_name, font_size)
        self._position = position or pg.Vector2(0, 0)

    def __call__(
        self,
        surface: pg.Surface,
        _sb: StencilBuffer,
        _v: Viewer,
    ) -> None:
        fps = self._clock.get_fps()
        color = "red"
        if fps >= self.YELLOW_LIMIT:
            color = "yellow"
        if fps >= self.GREEN_LIMIT:
            color = "green"

        fps_string = "{0:.0f}".format(fps)
        fps_image = self._font.render(fps_string, True, color)  # noqa: WPS425
        surface.blit(fps_image, self._position)


class WallRenderer(AbstractRenderer):
    """Render walls using ray marching(DDA) algorithm."""

    def __init__(self, map_: Map, viewer: Viewer) -> None:
        self._map = map_
        self._viewer = viewer  # ??? maybe use RenderContext?

        # FIXME: Use image loader instead of this garbage
        path1 = os.path.abspath("./assets/textures/1.png")
        path2 = os.path.abspath("./assets/textures/2.png")
        self._textures = [pg.image.load(path1), pg.image.load(path2)]

    def __call__(
        self, surface: pg.Surface, stencil: StencilBuffer, viewer: Viewer
    ) -> None:
        draw_walls(
            self._map,
            surface,
            stencil,
            self._textures,
            *self._viewer.position,
            self._viewer.angle,
            self._viewer.fov,
        )


class EntityRenderer(AbstractRenderer):
    """Render any entities."""

    def __init__(self) -> None:
        self._texture = pg.image.load("./assets/soldier.png")

    def __call__(
        self, surface: pg.Surface, stencil: StencilBuffer, viewer: Viewer
    ) -> None:
        """Render entity in entities list.

        :param surface: surface for rendering
        :param stencil: stencil buffer
        """
        draw_sprite(
            surface,
            stencil,
            self._texture,
            5,
            5,
            *viewer.position,
            viewer.angle,
            viewer.fov,
        )


class Pipeline:
    """Manipulate with renderers."""

    def __init__(
        self,
        viewer: Viewer,
        renderers: Collection[AbstractRenderer],
    ) -> None:
        self._viewer = viewer
        self._renderers = renderers

    def render(self, surface: pg.Surface) -> None:
        """Call all renderers.

        :param surface: surface for rendering
        """

        stencil = np.full(surface.get_width(), np.inf, dtype=np.float32)

        surface.fill("black")
        for renderer in self._renderers:
            renderer(surface, stencil, self._viewer)
        pg.display.flip()
