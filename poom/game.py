import os
from math import cos, sin, radians
from pathlib import Path
from typing import List

import pygame as pg
from pygame.math import Vector2

from poom.core import ray_march
from poom.map_loader import MapLoader
from poom.viewer import Viewer


SCREEN_SIZE = WIDTH, HEIGHT = 800, 600
FOV = radians(90)
root = Path(os.getcwd())


def game_loop() -> None:
    pg.init()
    screen = pg.display.set_mode(SCREEN_SIZE, vsync=1)

    player = Viewer(pg.Vector2(1.0, 1.0), radians(30))
    map_loader = MapLoader(root / "assets" / "levels")
    map_ = map_loader.load(1)

    run = True
    while run:
        # TODO: event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

        screen.fill("black")

        for x in range(WIDTH):
            alpha = x / WIDTH * FOV
            angle = player.angle - FOV / 2 + alpha

            dist = ray_march(map_, player.position, Vector2(cos(angle), sin(angle)))
            half_height = (
                int(HEIGHT / (dist * cos(angle - player.angle))) // 2
            )  # TODO: fix parabola-like walls
            pg.draw.line(
                screen,
                "white",
                (x, HEIGHT // 2 - half_height),
                (x, HEIGHT // 2 + half_height),
            )

        pg.display.flip()
    pg.quit()


def main(argv: List[str]) -> int:
    game_loop()
    return 0
