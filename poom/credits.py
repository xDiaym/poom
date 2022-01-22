from os import getcwd, listdir
from pathlib import Path
from typing import List, Union

import pygame as pg

root = Path(getcwd())


class Logo(pg.sprite.Sprite):
    def __init__(self, group: pg.sprite.Group, image: pg.Surface, start_x: int) -> None:
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.y = height - self.image.get_height() // 2 + 200
        self.rect.y = self.y

    def update(self, rate: float) -> None:
        self.rect.y = self.y - rate


class Text:
    def __init__(self) -> None:
        self.data = []

    def add(
        self, text: Union[str, List[str]], font_size: int, start_x: int, start_y: int
    ) -> None:
        self.data.append((text, font_size, start_x, start_y))

    def render(self, surface: pg.Surface, offset: float) -> None:
        for text, font_size, start_x, start_y in self.data:
            if isinstance(text, list):
                indent = 0
                for line in text:
                    font = pg.font.Font(root / "assets" / "font.ttf", font_size)
                    output = font.render(line, True, (255, 36, 0))
                    indent += output.get_height()
                    surface.blit(
                        output,
                        (
                            start_x - output.get_width() // 2,
                            start_y - output.get_height() // 2 + indent - offset,
                        ),
                    )

            else:
                font = pg.font.Font(root / "assets" / "font.ttf", font_size)
                output = font.render(text, True, (255, 36, 0))
                surface.blit(
                    output,
                    (
                        start_x - output.get_width() // 2,
                        start_y - output.get_height() // 2 - offset,
                    ),
                )


def logos_loader(scale) -> List[pg.Surface]:
    files = listdir(root / "assets" / "logo")
    images = []
    for logo in files:
        source = pg.image.load(root / "assets" / "logo" / logo).convert_alpha()
        img = pg.transform.scale(
            source, (source.get_width() * scale, source.get_height() * scale)
        )
        images.append(img)
    return images


def images_width(images: List[pg.Surface]):
    width = 0
    for image in images:
        width += image.get_width()
    return width


class Credits:
    def __init__(self) -> None:
        self.v = 30
        self.rate = 0
        self.text = Text()
        self.text.add("Poom", 100, width // 2, height + 50)
        self.text.add("Yandex.Lyceum project", 40, width // 2, height + 100)
        self.text.add(
            [
                "Developed by: Matthew Nekirov, Ilya Finatov",
                "Thanks for playing!",
            ],
            40,
            width // 2,
            height + 260,
        )
        self.group = pg.sprite.Group()
        logos = logos_loader(0.22)
        x = (width - images_width(logos)) // 2
        for i in range(len(logos)):
            Logo(self.group, logos[i], x)
            x += logos[i].get_width()

    def render(self, surface: pg.Surface):
        self.text.render(screen, self.rate)
        self.group.draw(surface)

    def update(self, dt: float):
        self.rate += self.v * dt
        self.group.update(self.rate)


# Test run
pg.init()
size = width, height = 1280, 720
screen = pg.display.set_mode(size)
pg.display.set_caption("Credits")
running = True
clock = pg.time.Clock()
final = Credits()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill("black")
    final.render(screen)
    final.update(clock.tick() / 1000)
    pg.display.update()
