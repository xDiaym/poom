import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

from poom.graphics import EntityRenderer, FPSRenderer, Pipeline, WallRenderer
from poom.map_loader import MapLoader
from poom.viewer import Viewer

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600
root = Path(os.getcwd())


def game_loop() -> None:
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(SCREEN_SIZE, vsync=1)

    player = Viewer(pg.Vector2(1.1, 1.1), radians(45), radians(90))
    map_loader = MapLoader(root / "assets" / "levels")
    map_ = map_loader.as_numpy(1)
    clock = pg.time.Clock()
    dt: float = 0
    pipeline = Pipeline(
        player,
        [WallRenderer(map_, player), FPSRenderer(clock), EntityRenderer()],
    )

    run = True
    while run:
        # TODO: event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            player._position += player.view_vector * dt * 5
        if keys[pg.K_s]:
            player._position -= player.view_vector * dt * 5
        if keys[pg.K_a]:
            player._angle -= dt * 5
        if keys[pg.K_d]:
            player._angle += dt * 5
        pipeline.render(screen)

        dt = clock.tick() / 1000
    pg.quit()


def main(argv: List[str]) -> int:
    game_loop()
    return 0
