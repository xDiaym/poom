"""All utils for graphics pipeline."""
import os
from abc import ABC, abstractmethod
from math import degrees
from pathlib import Path
from typing import Any, Collection, Final, Optional, Tuple, Union

import numpy as np
import pygame as pg
from numpy.typing import NDArray

from poom.entities import Entity, WithHealth
from poom.gun import AnimatedGun
from poom.level import Map
from poom.pooma.ray_march import draw_sprite, draw_walls  # pylint:disable=E0611
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


class BackgroundRenderer(AbstractRenderer):
    """Render sky and floor."""

    def __init__(self, skybox: pg.Surface, world_size: int) -> None:
        """Initialize object.

        :attr:`~BackgroundRenderer._world_size` is a width(or height) of map.
        It used as rotation coefficient.

        :param skybox: sky image
        :param world_size: size of world
        """
        self._skybox = skybox
        self._world_size = world_size
        self._floor_color = (40, 40, 40)

    def __call__(
        self,
        surface: pg.Surface,
        _: StencilBuffer,
        viewer: Viewer,
    ) -> None:
        """Draw background: floor and skybox.

        :param surface: surface for rendering
        :param _: unused
        :param viewer: camera-like object
        """
        self._render_skybox(surface, viewer)
        self._redener_floor(surface)

    def _render_skybox(self, surface: pg.Surface, viewer: Viewer) -> None:
        """Render skybox.

        Calculate offset using :attr:`~BackgroundRenderer._world_size`.

        :param surface: rendering surface(canvas)
        :param viewer: camera-like object
        """
        width = self._skybox.get_width()
        offset = -self._world_size * degrees(viewer.angle) % width
        for third in range(-1, 2):
            skybox_position = (offset + third * width, 0)
            surface.blit(self._skybox, skybox_position)

    def _redener_floor(self, surface: pg.Surface) -> None:
        """Render floor.

        :param surface: rendering surface(canvas)
        """
        width, height = surface.get_size()

        floor_position = (0, height // 2, width, height // 2)
        surface.fill(self._floor_color, floor_position)


class FPSRenderer(AbstractRenderer):
    """Displays colorized fps counter."""

    YELLOW_LIMIT: Final[int] = 30
    GREEN_LIMIT: Final[int] = 60

    def __init__(
        self,
        clock: pg.time.Clock,
        font_name: Optional[str] = None,
        font_size: int = 32,
        position: Optional[pg.Vector2] = None,
    ) -> None:
        self._clock = clock
        self._font = pg.font.Font(font_name, font_size)
        self._position = position or pg.Vector2(0, 0)

    def __call__(self, surface: pg.Surface, *args: Any, **kwargs: Any) -> None:
        fps = self._clock.get_fps()
        color = "red"
        if fps >= self.YELLOW_LIMIT:
            color = "yellow"
        if fps >= self.GREEN_LIMIT:
            color = "green"

        fps_string = "{0:.0f}".format(fps)
        fps_image = self._font.render(fps_string, True, color)  # noqa: WPS425
        surface.blit(fps_image, self._position)


root = Path(os.getcwd())


class HUDRenderer(AbstractRenderer):
    health_bar_length: Final[int] = 200
    health_bar_height: Final[int] = 30

    def __init__(self, with_health: WithHealth) -> None:
        self._with_health = with_health
        self._font = pg.font.Font(None, 30)

    def __call__(self, surface: pg.Surface, *args: Any, **kwargs: Any) -> None:
        width, height = surface.get_size()
        pg.draw.rect(
            surface,
            "black",
            (width * 0.7, height * 0.9, self.health_bar_length, self.health_bar_height),
        )
        pg.draw.rect(
            surface,
            "green",
            (
                width * 0.7 + 5,
                height * 0.9 + 5,
                (self.health_bar_length - 10) * self._with_health.get_health_ratio(),
                20,
            ),
        )
        percents = max(self._with_health.get_health(), 0)
        text = self._font.render(f"{percents} %", True, "red")
        text_x, text_y = (
            width * 0.7 + (self.health_bar_length - text.get_width()) * 0.5,
            height * 0.9 + (self.health_bar_height - text.get_height()) * 0.5,
        )
        surface.blit(text, (text_x, text_y))


ColorLike = Union[pg.Color, Tuple[int, int, int]]


class CrosshairRenderer(AbstractRenderer):
    """Render crosshair. Does not update the stencil buffer."""

    def __init__(
        self,
        color: ColorLike = (0, 255, 255),
        *,
        size: int = 7,
        width: int = 2,
    ) -> None:
        """Initialize renderer.

        :param color: crosshair color, defaults to (0, 255, 255)
        :param size: croshair width and height in pixels, defaults to 7
        :param width: line width, defaults to 2
        """
        self._color = color
        self._size = size
        self._width = width

    def __call__(
        self,
        surface: pg.Surface,
        _stencil: StencilBuffer,
        _viewer: Viewer,
    ) -> None:
        """Render crosshair on screen.

        Doesn't modify stencil buffer.

        :param surface: surface for rendering(canves)
        :param _stencil: unused
        :param _viewer: unused
        """
        width, height = surface.get_size()
        pg.draw.line(
            surface,
            self._color,
            (width // 2, height // 2 - self._size),
            (width // 2, height // 2 + self._size),
            self._width,
        )
        pg.draw.line(
            surface,
            self._color,
            (width // 2 - self._size, height // 2),
            (width // 2 + self._size, height // 2),
            self._width,
        )


class WallRenderer(AbstractRenderer):
    """Render walls using ray marching(DDA) algorithm."""

    def __init__(self, map_: Map, viewer: Viewer) -> None:
        """[summary]

        :param map_: [description]
        :type map_: Map
        :param viewer: [description]
        :type viewer: Viewer
        """
        self._map = map_
        self._viewer = viewer  # ??? maybe use RenderContext?

        # FIXME: Use image loader instead of this garbage
        path1 = os.path.abspath("./assets/textures/1.png")
        path2 = os.path.abspath("./assets/textures/2.png")
        self._textures = [pg.image.load(path1), pg.image.load(path2)]

    def __call__(
        self,
        surface: pg.Surface,
        stencil: StencilBuffer,
        viewer: Viewer,  # FIXME: self._viewer is useless now
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


def _render_single(
    surface: pg.Surface,
    stencil: StencilBuffer,
    viewer: Viewer,
    entity: Entity,
) -> None:
    draw_sprite(
        surface,
        stencil,
        entity.texture,
        *entity.position,
        *viewer.position,
        viewer.angle,
        viewer.fov,
    )


class EntityRenderer(AbstractRenderer):
    """Render any entities."""

    # TODO: create entity group for deletion from rendering
    def __init__(self, entities: Collection[Entity]) -> None:
        self._entities = entities

    def __call__(
        self,
        surface: pg.Surface,
        stencil: StencilBuffer,
        viewer: Viewer,
    ) -> None:
        """Render entity in entities list.

        :param surface: surface for rendering
        :param stencil: stencil buffer
        :param viewer: camera-like object
        """
        start = viewer.position
        entities = sorted(
            self._entities,
            # Avoid sqrt calculation
            key=lambda entity: (entity.position - start).magnitude_squared(),
            reverse=True,
        )

        # Due to the fact that 1D depth buffer is used,
        # the attributes must be drawn in decreasing order of distance.
        for entity in entities:  # noqa: WPS440 no overlap
            _render_single(surface, stencil, viewer, entity)


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


class GunRenderer(AbstractRenderer):
    def __init__(self, gun: AnimatedGun) -> None:
        self._gun = gun

    def __call__(
        self, surface: pg.Surface, _stencil: StencilBuffer, _viewer: Viewer
    ) -> None:
        texture = self._gun.texture
        s_width, s_height = surface.get_size()
        t_width, t_height = texture.get_size()
        surface.blit(texture, ((s_width - t_width) // 2, s_height - t_height))
