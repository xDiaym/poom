import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

from poom.graphics import FPSRenderer, Pipeline, WallRenderer
from poom.map_loader import MapLoader
from poom.viewer import Viewer

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600
root = Path(os.getcwd())


def game_loop() -> None:
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(SCREEN_SIZE, vsync=1)

    player = Viewer(pg.Vector2(1.0, 1.0), radians(45), radians(90))
    map_loader = MapLoader(root / "assets" / "levels")
    map_ = map_loader.as_numpy(1)
    clock = pg.time.Clock()

    pipeline = Pipeline([WallRenderer(map_, player), FPSRenderer(clock)])

    run = True
    while run:
        # TODO: event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        player._position += pg.Vector2(0.01, 0.01)

        pipeline.render(screen)

        clock.tick()
    pg.quit()


def main(argv: List[str]) -> int:
    game_loop()
    return 0
