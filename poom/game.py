import os
import time
from math import radians
from pathlib import Path
from typing import List

import pygame as pg
from pygame.event import Event

from poom.credits import Credits
from poom.records import Record, update_record
from poom.settings import ROOT
from poom.shared import SceneContext, Settings

pg.mixer.init()  # noqa

import poom.shared as shared
from poom.graphics import (
    BackgroundRenderer,
    CrosshairRenderer,
    EntityRenderer,
    FPSRenderer,
    GunRenderer,
    HUDRenderer,
    Pipeline,
    WallRenderer,
)
from poom.gun import create_animated_gun
from poom.level import Level
from poom.main_menu import WelcomeScene
from poom.npc import Enemy
from poom.player import Player

root = Path(os.getcwd())
clock = pg.time.Clock()


class LevelScene(shared.AbstractScene):
    def __init__(self, context: shared.SceneContext) -> None:
        super().__init__(context)
        level = Level.from_dir(root / "assets" / "levels" / "1")
        self.map_ = level.map_

        animated_gun = create_animated_gun(
            self.map_,
            2,
            25,
            root / "assets" / "sprites" / "gun",
            2,
        )
        self._start_time = time.time()
        self._enemies: List[Enemy] = []
        self._player = Player(
            map_=self.map_,
            gun=animated_gun,
            position=pg.Vector2(1.1, 1.1),
            angle=radians(45),
            fov=radians(90),
            enemies=self._enemies,
        )
        self._player.on_death(self._on_lose)

        enemy_texture = pg.image.load(
            root / "assets" / "sprites" / "front_attack" / "0.png"
        )
        for position in level.enemies_positions:
            enemy = Enemy(
                texture=enemy_texture,
                map_=level.map_,
                entities=self._enemies,
                ai_enemy=self._player,
                position=position,
                angle=radians(45),
                fov=radians(90),
            )
            self._enemies.append(enemy)

        self._renderers = [
            BackgroundRenderer(
                pg.image.load(root / "assets" / "textures" / "skybox.png"),
                self.map_.shape[0],
            ),
            WallRenderer(self.map_, self._player),
            EntityRenderer(self._enemies),
            CrosshairRenderer(),
            FPSRenderer(clock),
            GunRenderer(animated_gun),
            HUDRenderer(self._player),
        ]
        self._pipeline = Pipeline(self._player, self._renderers)

    def on_event(self, events: List[Event]) -> None:
        pass

    def render(self) -> None:
        self._pipeline.render(self._context.screen)

    def update(self, dt: float) -> None:
        if len(self._enemies) == 0:
            self._on_win()

        self._player.update(dt)
        for npc in self._enemies:
            npc.update(dt)

    def _on_lose(self) -> None:
        self._context.scene = WelcomeScene(self._context)

    def _on_win(self) -> None:
        record = Record(
            game_time=time.time() - self._start_time,
            health=self._player.get_health(),
        )
        update_record(ROOT / "assets" / "records.json", record)

        self._context.scene = Credits(self._context)


class Game:
    def __init__(self) -> None:
        self._init()
        self._run = True
        self._settings = Settings(ROOT)
        self._screen = pg.display.set_mode(self._settings.screen_size, vsync=1)

    def stop(self) -> None:
        self._run = False

    def run(self) -> None:
        sc = SceneContext(self._screen, self)
        sc.scene = WelcomeScene(sc)
        clock = pg.time.Clock()
        dt: float = 0

        while self._run:
            # TODO: event handler
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self._run = False
                if event.type == pg.WINDOWMINIMIZED:
                    pg.mixer.music.pause()
                if event.type == pg.WINDOWRESTORED:
                    pg.mixer.music.unpause()
            sc.on_event(events)
            sc.render()
            dt = clock.tick() / 1000
            sc.update(dt)
        self._deinit()

    def _init(self) -> None:
        pg.init()
        pg.font.init()

    def _deinit(self) -> None:
        self._settings.update(ROOT)
        pg.quit()


def main(argv: List[str]) -> int:
    game = Game()
    game.run()
    return 0
