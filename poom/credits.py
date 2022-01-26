from dataclasses import dataclass
import operator
from os import listdir
from pathlib import Path
from textwrap import dedent
from typing import Collection, Final, List, cast

import pygame as pg
from pygame.event import Event
from pygame.font import Font
from pygame.sprite import Group

from poom.settings import ROOT
from poom.shared import AbstractScene, SceneContext


def logos_loader(path: Path, scale: float = 1) -> List[pg.Surface]:
    """Load all files in directory as pygame's surfaces.

    :param path: path to directory
    :param scale: image scale factor
    :return: list of scaled images
    """
    files = listdir(path)
    images: List[pg.Surface] = []
    for logo in files:
        source = pg.image.load(path / logo).convert_alpha()
        image = pg.transform.scale(
            source,
            (source.get_width() * scale, source.get_height() * scale),
        )
        images.append(cast(pg.Surface, image))
    return images


def images_width(images: List[pg.Surface]) -> int:
    """Calculate sum of pygame surfaces width.

    :param images: list of surface
    :return: sum of widths.
    """
    return sum(map(operator.methodcaller("get_width"), images))


class FloatingSurface(pg.sprite.Sprite):
    speed: Final[float] = -30

    def __init__(
        self,
        group: Group,
        surface: pg.Surface,
        position: pg.Vector2,
    ) -> None:
        super().__init__(group)
        self.image = surface
        self._y_position = position.y
        self.rect = self.image.get_rect()
        self.rect.x = int(position.x)
        self.rect.y = int(position.y)

    def update(self, dt: float) -> None:
        self._y_position += self.speed * dt
        self.rect.y = int(self._y_position)


def create_text(
    text: str,
    font: Font,
    group: Group,
    start_y: int,
    screen_width: int,
    interval: int = 5,
) -> None:
    y_position = start_y 
    for line in text.split("\n"):
        surface = font.render(line, True, (255, 36, 0))
        left = (screen_width - surface.get_width()) // 2
        FloatingSurface(group, surface, pg.Vector2(left, y_position))
        y_position += surface.get_height() + interval


def load_logos(
    path: Path,
    group: Group,
    start_y: int,
    screen_width: int,
    scale: float = 1
) -> None:
    logos = logos_loader(path, scale)

    width = images_width(logos)
    max_height = max(map(operator.methodcaller("get_height"), logos))
    surface = pg.Surface((width, max_height), pg.SRCALPHA)

    x = 0
    for logo in logos:
        y = (max_height - logo.get_height()) // 2
        surface.blit(logo, (x, y))
        x += logo.get_width()

    surface_x = (screen_width - width) // 2
    FloatingSurface(group, surface, pg.Vector2(surface_x, start_y))



TEXT = dedent("""
Developed by: Matthew Nekirov, Ilya Finatov
Thanks for playing!
""")

class Credits(AbstractScene):
    def __init__(self, context: "SceneContext") -> None:
        super().__init__(context)
        screen_size = context.screen.get_size()
        self._group = Group()
        self._bacground = pg.image.load(
            ROOT / "assets" / "textures" / "back.png",
        )
        self._bacground = pg.transform.scale(
            self._bacground,
            screen_size,
        )
        # TODO: make x autoincrement
        big_font = Font(ROOT / "assets" / "font.ttf", 100)
        font = Font(ROOT / "assets" / "font.ttf", 40)

        create_text("Poom", big_font, self._group, screen_size[1], screen_size[0])
        create_text("Yandex.Lyceum project", font, self._group, screen_size[1] + 120, screen_size[0])

        load_logos(ROOT / "assets" / "logo", self._group, screen_size[1] + 250, screen_size[0], 0.22)

        create_text(TEXT, font, self._group, screen_size[1] + 400, screen_size[0])


    def render(self) -> None:
        self._context.screen.blit(self._bacground, (0, 0))
        self._group.draw(self._context.screen)
        pg.display.flip()

    def update(self, dt: float):
        self._group.update(dt)

    def on_event(self, event: Collection[Event]) -> None:
        # Do nothing.
        pass
