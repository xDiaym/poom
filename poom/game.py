import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

from poom.entities.enemy import Enemy
from poom.player import Player
from poom.graphics import (
    BackgroundRenderer,
    CrosshairRenderer,
    EntityRenderer,
    FPSRenderer,
    Pipeline,
    WallRenderer,
)
from poom.map_loader import MapLoader

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600
root = Path(os.getcwd())


def game_loop() -> None:
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(SCREEN_SIZE, vsync=1)

    map_loader = MapLoader(root / "assets" / "levels")
    map_ = map_loader.as_numpy(1)
    player = Player(map_=map_, position=pg.Vector2(1.1, 1.1), angle=radians(45), fov=radians(90))
    clock = pg.time.Clock()
    dt: float = 0

    soldier1 = Enemy(
        position=pg.Vector2(5, 5),
        angle=radians(45),
        fov=radians(90),
        texture=pg.image.load("assets/soldier.png"),
    )
    soldier2 = Enemy(
        position=pg.Vector2(5.25, 4),
        angle=radians(45),
        fov=radians(90),
        texture=pg.image.load("assets/soldier.png"),
    )
    renderers = [
        BackgroundRenderer(pg.image.load("assets/skybox.png"), map_.shape[0]),
        WallRenderer(map_, player),
        EntityRenderer([soldier1, soldier2]),
        CrosshairRenderer(),
        FPSRenderer(clock),
    ]
    pipeline = Pipeline(player, renderers)

    run = True
    while run:
        # TODO: event handler
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
        player.update(dt, events)
        pipeline.render(screen)
        dt = clock.tick() / 1000
    pg.quit()


def main(argv: List[str]) -> int:
    game_loop()
    return 0
