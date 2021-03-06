import time
from math import radians
from typing import List

import pygame as pg
from pygame.event import Event

pg.mixer.init()  # noqa

import poom.shared as shared
from poom.ai.enemy import Enemy
from poom.credits import Credits
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
from poom.gun.player_gun import create_player_gun
from poom.level import Level
from poom.main_menu import WelcomeScene
from poom.player import Player
from poom.records import Record, update_record
from poom.settings import ROOT
from poom.shared import SceneContext, Settings

clock = pg.time.Clock()
settings = Settings.load(ROOT)


class LevelScene(shared.AbstractScene):
    level = 1

    def __init__(self, context: shared.SceneContext) -> None:
        super().__init__(context)
        level = Level.from_dir(ROOT / "assets" / "levels" / f"{self.level}")
        sound = pg.mixer.Sound(ROOT / "assets" / "sounds" / f"level{self.level}.mp3")
        self.channel = pg.mixer.Channel(5)
        self.channel.set_volume(settings.volume / 100)
        self.map_ = level.map_

        player_gun = create_player_gun(
            self.map_,
            2,
            25,
            ROOT / "assets" / "sprites" / "gun",
            2,
        )
        self._start_time = time.time()
        self._enemies: List[Enemy] = []
        self._player = Player(
            map_=self.map_,
            gun=player_gun,
            position=pg.Vector2(1.1, 1.1),
            angle=radians(45),
            fov=radians(90),
            enemies=self._enemies,
        )
        self._player.on_death(self._on_lose)

        enemy_texture = pg.image.load(
            ROOT / "assets" / "sprites" / "front_attack" / "0.png"
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
                pg.image.load(ROOT / "assets" / "textures" / f"skybox{self.level}.png"),
                self.map_.shape[0],
            ),
            WallRenderer(self.map_, self._player),
            EntityRenderer(self._enemies),
            CrosshairRenderer(),
            GunRenderer(player_gun),
            HUDRenderer(self._player),
        ]
        if settings.fps_tick:
            self._renderers.append(FPSRenderer(clock))
        self.channel.play(sound)
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
        self.channel.stop()
        self._context.scene = WelcomeScene(self._context)

    def _on_win(self) -> None:
        LevelScene.level += 1
        if LevelScene.level > 3:
            record = Record(
                game_time=time.time() - self._start_time,
                health=self._player.get_health(),
            )
            update_record(ROOT / "assets" / "records.json", record)
            self._context.scene = Credits(self._context)
        else:
            self._context.scene = LevelScene(self._context)


class Game:
    def __init__(self) -> None:
        self._init()
        self._run = True
        self._screen = pg.display.set_mode(settings.screen_size, vsync=1)

    def stop(self) -> None:
        self._run = False

    def run(self) -> None:
        sc = SceneContext(self._screen, self)
        sc.scene = WelcomeScene(sc)

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
        pg.display.set_caption("Poom")
        icon = pg.image.load(ROOT / "assets" / "textures" / "icon.ico")
        pg.display.set_icon(icon)

    def _deinit(self) -> None:
        pg.quit()


def main(argv: List[str]) -> int:
    game = Game()
    game.run()
    return 0
