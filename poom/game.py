import json
import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

import poom.main_menu as menu
import poom.shared as shared
from poom.animated import Animation
from poom.entities import Enemy
from poom.graphics import (
    BackgroundRenderer,
    CrosshairRenderer,
    EntityRenderer,
    FPSRenderer,
    GunRenderer,
    Pipeline,
    WallRenderer,
)
from poom.gun import AnimatedGun, Gun
from poom.map_loader import MapLoader
from poom.player import Player

# screen = pg.display.set_mode(settings.screen_size, vsync=1)
root = Path(os.getcwd())
clock = pg.time.Clock()


class GameScene(shared.AbstractScene):
    def __init__(self, context=shared.SceneContext):
        super().__init__(context)
        # self.screen = screen
        self.map_loader = MapLoader(root / "assets" / "levels")
        self.map_ = self.map_loader.as_numpy(1)

        self.gun = Gun(self.map_, 2, 25)
        self.animated_gun = AnimatedGun(
            self.gun,
            Animation.from_dir(Path("assets/gun"), 10, 2),
        )

        self.enemies = []
        self.player = Player(
            map_=self.map_,
            gun=self.animated_gun,
            position=pg.Vector2(1.1, 1.1),
            angle=radians(45),
            fov=radians(90),
            enemies=self.enemies,
        )

        self.source = pg.image.load(root / "assets" / "front_attack" / "0.png")
        self.soldier2 = Enemy(
            position=pg.Vector2(8.5, 8.5),
            angle=radians(45),
            fov=radians(90),
            texture=self.source,
            map_=self.map_,
            enemy=self.player,
        )
        self.enemies.append(self.soldier2)

        self.renderers = [
            BackgroundRenderer(
                pg.image.load(root / "assets" / "skybox.png"), self.map_.shape[0]
            ),
            WallRenderer(self.map_, self.player),
            EntityRenderer([self.soldier2]),
            CrosshairRenderer(),
            FPSRenderer(clock),
            GunRenderer(self.animated_gun),
        ]
        self.pipeline = Pipeline(self.player, self.renderers)

    def on_event(self, events) -> None:
        pass

    def render(self) -> None:
        self.pipeline.render(self._context.screen)

    def update(self, dt: float) -> None:
        self.player.update(dt)
        for npc in self.enemies:
            npc.update(dt)


def game_loop() -> None:
    pg.init()
    pg.font.init()

    settings = shared.Settings(root)
    screen = pg.display.set_mode(settings.screen_size, vsync=1)
    sc = shared.SceneContext(menu.WelcomeScene, screen)
    clock = pg.time.Clock()
    run = True
    while run:
        # TODO: event handler
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.WINDOWMINIMIZED:
                pg.mixer.music.pause()
            if event.type == pg.WINDOWRESTORED:
                pg.mixer.music.unpause()
        sc.on_event(events)
        sc.render()
        dt = clock.tick() / 1000
        sc.update(dt)
    pg.quit()
    settings.update(root)


def main(argv: List[str]) -> int:
    game_loop()
    return 0
