import os
from math import radians
from pathlib import Path
from typing import List

import pygame as pg

import poom.main_menu as menu
import poom.shared as shared
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
from poom.gun import create_animated_gun
from poom.level import Level
from poom.player import Player

# screen = pg.display.set_mode(settings.screen_size, vsync=1)
root = Path(os.getcwd())
clock = pg.time.Clock()


class GameScene(shared.AbstractScene):
    def __init__(self, context=shared.SceneContext):
        super().__init__(context)
        # self.screen = screen
        level = Level.from_dir(root / "assets" / "levels" / "1")
        self.map_ = level.map_

        animated_gun = create_animated_gun(self.map_, 2, 25, root / "assets" / "gun", 2)

        self.enemies = []
        self.player = Player(
            map_=self.map_,
            gun=animated_gun,
            position=pg.Vector2(1.1, 1.1),
            angle=radians(45),
            fov=radians(90),
            enemies=self.enemies,
        )

        enemy_texture = pg.image.load(root / "assets" / "front_attack" / "0.png")
        for position in level.enemies_positions:
            enemy = Enemy(
                position=position,
                angle=radians(45),
                fov=radians(90),
                texture=enemy_texture,
                map_=level.map_,
                enemy=self.player,
            )
            self.enemies.append(enemy)

        self.renderers = [
            BackgroundRenderer(
                pg.image.load(root / "assets" / "skybox.png"), self.map_.shape[0]
            ),
            WallRenderer(self.map_, self.player),
            EntityRenderer(self.enemies),
            CrosshairRenderer(),
            FPSRenderer(clock),
            GunRenderer(animated_gun),
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
    dt: float = 0

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
