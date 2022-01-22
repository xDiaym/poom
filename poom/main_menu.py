import json
from os import getcwd, listdir
from pathlib import Path

import pygame as pg
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import (
    UIButton,
    UIDropDownMenu,
    UIHorizontalSlider,
    UILabel,
    UITextBox,
)
from shared import AbstractScene, Animation, SceneContext, ScreenResizer

# "#2f353b"
pg.init()
root = Path(getcwd())
print(root)
with open(root / "assets" / "settings.json") as file:
    settings = json.load(file)
screen = ScreenResizer(*settings["screen_size"], root)
pg.display.set_caption("Greeting")
running = True
clock = pg.time.Clock()


def clamp(low: int, high: int, value: float):
    return max(min(high, value), low)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Zombie(pg.sprite.Sprite, metaclass=Singleton):
    def __init__(self) -> None:
        self.group = pg.sprite.GroupSingle()
        super().__init__(self.group)
        self.v = 30
        self.walking_animation = Animation.from_dir(
            root / "assets" / "zombie" / "walk", 3, 0.1875
        )
        self.rotation_animation = Animation.from_dir(
            root / "assets" / "zombie" / "rotate", 3, 0.1875
        )
        self.image = self.walking_animation.current_frame
        self.rect = self.image.get_rect()
        self.rect.x = screen.width - self.image.get_width()
        self.rect.y = screen.height - self.image.get_height()
        self.x = self.rect.x
        self.rotate = False
        self.left = True

    def update(self, dt: float) -> None:
        if not 0 < self.x <= screen.width - self.image.get_width() and not self.rotate:
            self.rotate = True
            self.rotation_animation.reset()
        if not self.rotate:
            self.x -= self.v * dt
            self.rect.x = self.x
            self.walking_animation.update(dt)
            self.image = self.walking_animation.current_frame
        else:
            if not self.rotation_animation.done:
                self.rotation_animation.update(dt)
                self.image = self.rotation_animation.current_frame
            else:
                self.walking_animation.flip_images()
                self.rotation_animation.flip_images()
                self.v = -self.v
                self.x = clamp(1, screen.width - self.image.get_width() - 1, self.x)
                self.left = not self.left
                self.rotate = False


class WelcomeScene(AbstractScene):
    def __init__(self, context: SceneContext) -> None:
        super().__init__(context)
        self.zombie = Zombie()
        self.poom_label = UILabel(
            pg.Rect((screen.width - 220) // 2, screen.height * 0.05, 220, 110),
            "Poom",
            screen.manager,
            object_id=ObjectID(object_id="#poom"),
        )
        self.play = UIButton(
            pg.Rect((screen.width - 160) // 2, screen.height * 0.3, 160, 70),
            "Play",
            screen.manager,
        )
        self.settings = UIButton(
            pg.Rect((screen.width - 160) // 2, screen.height * 0.4, 160, 70),
            "Settings",
            screen.manager,
        )
        self.statistics = UIButton(
            pg.Rect((screen.width - 160) // 2, screen.height * 0.5, 160, 70),
            "Statistics",
            screen.manager,
        )
        self.quit = UIButton(
            pg.Rect((screen.width - 160) // 2, screen.height * 0.6, 160, 70),
            "Quit",
            screen.manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            screen.manager.clear_and_reset()
            if event.ui_element == self.play:
                print("play")
            if event.ui_element == self.settings:
                self._context.scene = SettingsScene(self._context)
            if event.ui_element == self.statistics:
                self._context.scene = StatiscticsScene(self._context)
            if event.ui_element == self.quit:
                print("quit")

    def render(self, surface: pg.Surface) -> None:
        self.zombie.group.draw(surface)
        screen.manager.draw_ui(surface)

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        screen.manager.update(0)


class SettingsScene(AbstractScene):
    def __init__(self, context: SceneContext) -> None:
        super().__init__(context)
        self.zombie = Zombie()
        self.settings_label = UILabel(
            pg.Rect((screen.width - 230) // 2, screen.height * 0.05, 230, 80),
            "Settings",
            screen.manager,
        )
        self.back = UIButton(
            pg.Rect(screen.width * 0.05, screen.height * 0.075, 50, 50),
            "X",
            screen.manager,
        )
        self.graphics_lbl = UILabel(
            pg.Rect((screen.width - 200) // 2, screen.height * 0.23, 100, 50),
            "Quality:",
            screen.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.graphics = UIDropDownMenu(
            ["Low", "Medium", "High"],
            settings["quality"],
            pg.Rect((screen.width - 200) // 2, screen.height * 0.23 + 40, 200, 50),
            screen.manager,
        )
        self.screen_size_lbl = UILabel(
            pg.Rect((screen.width - 200) // 2, screen.height * 0.4, 150, 50),
            "Screen size:",
            screen.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.screen_size = UIDropDownMenu(
            ["800x600 (4:3)", "1024x768 (4:3)", "1280x720 (16:9)"],
            f"{screen.width}x{screen.height} ({settings['ratio']})",
            pg.Rect((screen.width - 200) // 2, screen.height * 0.4 + 40, 290, 50),
            screen.manager,
        )
        self.volume_lbl = UILabel(
            pg.Rect((screen.width - 200) // 2, screen.height * 0.58, 100, 50),
            "Volume:",
            screen.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.volume = UIHorizontalSlider(
            pg.Rect((screen.width - 200) // 2, screen.height * 0.58 + 40, 270, 30),
            settings["volume"] / 100,
            range(101),
            screen.manager,
        )
        self.current_volume = UILabel(
            pg.Rect(
                (screen.width - 200) // 2 + 260,
                screen.height * 0.58 + 32,
                100,
                50,
            ),
            f"{settings['volume']} %",
            screen.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.fps_lbl = UILabel(
            pg.Rect((screen.width - 200) // 2, screen.height * 0.71, 100, 50),
            "Fps tick:",
            screen.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.fps = UIDropDownMenu(
            ["on", "off"],
            "off" if not settings["fps_tick"] else "on",
            pg.Rect((screen.width - 200) // 2, screen.height * 0.71 + 40, 150, 50),
            screen.manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self.current_volume.set_text(f"{int(self.volume.current_value * 100)} %")
            settings["volume"] = int(self.volume.current_value * 100)
            pg.mixer.music.set_volume(self.volume.current_value)
            with open(root / "assets" / "settings.json", "w") as file:
                json.dump(settings, file)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back:
                screen.manager.clear_and_reset()
                self._context.scene = WelcomeScene(self._context)
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.graphics:
                settings["quality"] = self.graphics.selected_option
                with open(root / "assets" / "settings.json", "w") as file:
                    json.dump(settings, file)
            if event.ui_element == self.screen_size:
                new_size, ratio = self.screen_size.selected_option.split()
                width, height = map(int, new_size.split("x"))
                screen.resize(width, height, root)
                self.zombie.rect.y = height - self.zombie.image.get_height()
                settings["screen_size"] = [width, height]
                settings["ratio"] = ratio[1:-1]
                self._context.scene = SettingsScene(self._context)
            if event.ui_element == self.fps:
                settings["fps_tick"] = (
                    True if self.fps.selected_option == "on" else False
                )
            with open(root / "assets" / "settings.json", "w") as file:
                json.dump(settings, file)

    def render(self, surface: pg.Surface) -> None:
        self.zombie.group.draw(surface)
        screen.manager.draw_ui(surface)

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        screen.manager.update(0)


class StatiscticsScene(AbstractScene):
    def __init__(self, context: SceneContext) -> None:
        super().__init__(context)
        self.zombie = Zombie()
        self.stats_label = UILabel(
            pg.Rect((screen.width - 230) // 2, screen.height * 0.05, 230, 80),
            "Statistics",
            screen.manager,
        )
        self.back = UIButton(
            pg.Rect(screen.width * 0.05, screen.height * 0.075, 50, 50),
            "X",
            screen.manager,
        )
        self.stats = UITextBox(
            "1 level:<br>    Kills: 1023<br>    Damage: 800",
            pg.Rect(
                screen.width * 0.2,
                screen.height * 0.3,
                screen.width * 0.6,
                screen.height * 0.5,
            ),
            screen.manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back:
                screen.manager.clear_and_reset()
                self._context.scene = WelcomeScene(self._context)

    def render(self, surface: pg.Surface) -> None:
        self.zombie.group.draw(surface)
        screen.manager.draw_ui(surface)

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        screen.manager.update(0)


sc = SceneContext(WelcomeScene)
pg.mixer.init()
pg.mixer.music.load(root / "assets" / "main.mp3")
pg.mixer.music.set_volume(settings["volume"] / 100)
pg.mixer.music.play(-1)

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.WINDOWMINIMIZED:
            pg.mixer.music.pause()
        if event.type == pg.WINDOWRESTORED:
            pg.mixer.music.unpause()
        sc.handler(event)
        screen.manager.process_events(event)
    sc.render(screen, clock)

    pg.display.update()
