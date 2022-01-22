import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

from poom.animated import Animation
from poom.entities import Enemy
from poom.graphics import (
    BackgroundRenderer,
    CrosshairRenderer,
    EntityRenderer,
    FPSRenderer,
    Pipeline,
    WallRenderer, GunRenderer,
)
from poom.gun import AnimatedGun, Gun
from poom.map_loader import MapLoader
from poom.player import Player

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600
root = Path(os.getcwd())


def game_loop() -> None:
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(SCREEN_SIZE, vsync=1)

    map_loader = MapLoader(root / "assets" / "levels")
    map_ = map_loader.as_numpy(1)
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
    enemies = [soldier1, soldier2]

    gun = Gun(map_, 1, 25)
    animated_gun = AnimatedGun(
        gun,
        Animation.from_dir(Path("assets/gun"), 10, 2),
    )
    player = Player(
        map_=map_,
        gun=animated_gun,
        position=pg.Vector2(1.1, 1.1),
        angle=radians(45),
        fov=radians(90),
        enemies=enemies,
    )
    renderers = [
        BackgroundRenderer(pg.image.load("assets/skybox.png"), map_.shape[0]),
        WallRenderer(map_, player),
        EntityRenderer(enemies),
        CrosshairRenderer(),
        FPSRenderer(clock),
        GunRenderer(animated_gun),
    ]
    pipeline = Pipeline(player, renderers)

    run = True
    while run:
        # TODO: event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        player.update(dt)
        pipeline.render(screen)
        dt = clock.tick() / 1000
    pg.quit()


def main(argv: List[str]) -> int:
    game_loop()
    return 0
