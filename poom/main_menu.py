from os import getcwd
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

import poom.game as game
import poom.shared as shared
from poom.animated import Animation

root = Path(getcwd())
settings = shared.Settings(root)


def clamp(low: int, high: int, value: float):
    return max(min(high, value), low)


class Zombie(pg.sprite.Sprite, metaclass=shared.Singleton):
    def __init__(self, screen: pg.Surface) -> None:
        self.group = pg.sprite.GroupSingle()
        super().__init__(self.group)
        self.screen = screen
        self.v = 30
        self.walking_animation = Animation.from_dir(
            root / "assets" / "zombie" / "walk", 0.75, 0.1875
        )
        self.rotation_animation = Animation.from_dir(
            root / "assets" / "zombie" / "rotate", 0.75, 0.1875
        )
        self.image = self.walking_animation.current_frame
        self.rect = self.image.get_rect()
        self.rect.x = screen.get_width() - self.image.get_width()
        self.rect.y = screen.get_height() - self.image.get_height()
        self.x = self.rect.x
        self.rotate = False
        self.left = True

    def update(self, dt: float) -> None:
        if (
            not 0 < self.x <= self.screen.get_width() - self.image.get_width()
            and not self.rotate
        ):
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
                self.x = clamp(
                    1, self.screen.get_width() - self.image.get_width() - 1, self.x
                )
                self.left = not self.left
                self.rotate = False


class WelcomeScene(shared.AbstractScene):
    def __init__(self, context: shared.SceneContext) -> None:
        super().__init__(context)
        self.screen = self._context.screen
        self.manager = pygame_gui.UIManager(
            self.screen.get_size(), root / "assets" / "style.json"
        )
        self.zombie = Zombie(self.screen)
        width, height = self.screen.get_width(), self.screen.get_height()
        self.background = pg.transform.scale(
            pg.image.load(root / "assets" / "back.png").convert_alpha(),
            (width, height),
        )
        self.poom_label = UILabel(
            pg.Rect((width - 220) // 2, height * 0.05, 220, 110),
            "Poom",
            self.manager,
            object_id=ObjectID(object_id="#poom"),
        )
        self.play = UIButton(
            pg.Rect((width - 160) // 2, height * 0.3, 160, 70),
            "Play",
            self.manager,
        )
        self.settings = UIButton(
            pg.Rect((width - 160) // 2, height * 0.4, 160, 70),
            "Settings",
            self.manager,
        )
        self.statistics = UIButton(
            pg.Rect((width - 160) // 2, height * 0.5, 160, 70),
            "Statistics",
            self.manager,
        )
        self.quit = UIButton(
            pg.Rect((width - 160) // 2, height * 0.6, 160, 70),
            "Quit",
            self.manager,
        )

    def on_event(self, events) -> None:
        for event in events:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play:
                    self._context.scene = game.GameScene(self._context)
                if event.ui_element == self.settings:
                    self._context.scene = SettingsScene(self._context)
                if event.ui_element == self.statistics:
                    self._context.scene = StatiscticsScene(self._context)
                if event.ui_element == self.quit:
                    print("quit")
            self.manager.process_events(event)

    def render(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.zombie.group.draw(self.screen)
        self.manager.draw_ui(self.screen)
        pg.display.flip()

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        self.manager.update(0)


class SettingsScene(shared.AbstractScene):
    def __init__(self, context: shared.SceneContext) -> None:
        print("hello")
        super().__init__(context)
        self.screen = self._context.screen
        self.manager = pygame_gui.UIManager(
            self.screen.get_size(), root / "assets" / "style.json"
        )
        self.zombie = Zombie(self.screen)
        width, height = self.screen.get_width(), self.screen.get_height()
        self.background = pg.transform.scale(
            pg.image.load(root / "assets" / "back.png").convert_alpha(),
            (width, height),
        )
        self.settings_label = UILabel(
            pg.Rect((width - 230) // 2, height * 0.05, 230, 80),
            "Settings",
            self.manager,
        )
        self.back = UIButton(
            pg.Rect(width * 0.05, height * 0.075, 50, 50),
            "X",
            self.manager,
        )
        self.graphics_lbl = UILabel(
            pg.Rect((width - 200) // 2, height * 0.23, 100, 50),
            "Quality:",
            self.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.graphics = UIDropDownMenu(
            ["Low", "Medium", "High"],
            settings.quality,
            pg.Rect((width - 200) // 2, height * 0.23 + 40, 200, 50),
            self.manager,
        )
        self.screen_size_lbl = UILabel(
            pg.Rect((width - 200) // 2, height * 0.4, 150, 50),
            "Screen size:",
            self.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.screen_size = UIDropDownMenu(
            ["800x600 (4:3)", "1024x768 (4:3)", "1280x720 (16:9)"],
            f"{width}x{height} ({settings.ratio})",
            pg.Rect((width - 200) // 2, height * 0.4 + 40, 290, 50),
            self.manager,
        )
        self.volume_lbl = UILabel(
            pg.Rect((width - 200) // 2, height * 0.58, 100, 50),
            "Volume:",
            self.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.volume = UIHorizontalSlider(
            pg.Rect((width - 200) // 2, height * 0.58 + 40, 270, 30),
            settings.volume / 100,
            range(101),
            self.manager,
        )
        self.current_volume = UILabel(
            pg.Rect(
                (width - 200) // 2 + 260,
                height * 0.58 + 32,
                100,
                50,
            ),
            f"{settings.volume} %",
            self.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.fps_lbl = UILabel(
            pg.Rect((width - 200) // 2, height * 0.71, 100, 50),
            "Fps tick:",
            self.manager,
            object_id=ObjectID(object_id="#sublabel"),
        )
        self.fps = UIDropDownMenu(
            ["on", "off"],
            "off" if not settings.fps_tick else "on",
            pg.Rect((width - 200) // 2, height * 0.71 + 40, 150, 50),
            self.manager,
        )

    def on_event(self, events) -> None:
        for event in events:
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                self.current_volume.set_text(
                    f"{int(self.volume.current_value * 100)} %"
                )
                settings.volume = int(self.volume.current_value * 100)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back:
                    self._context.scene = WelcomeScene(self._context)
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.graphics:
                    settings.quality = self.graphics.selected_option
                if event.ui_element == self.screen_size:
                    new_size, ratio = self.screen_size.selected_option.split()
                    width, height = map(int, new_size.split("x"))
                    settings.screen_size = [width, height]
                    settings.ratio = ratio[1:-1]
                    self._context.scene = SettingsScene(self._context)
                if event.ui_element == self.fps:
                    settings.fps_tick = (
                        True if self.fps.selected_option == "on" else False
                    )
            self.manager.process_events(event)

    def render(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.zombie.group.draw(self.screen)
        self.manager.draw_ui(self.screen)
        pg.display.flip()

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        self.manager.update(0)


class StatiscticsScene(shared.AbstractScene):
    def __init__(self, context: shared.SceneContext) -> None:
        super().__init__(context)
        self.screen = self._context.screen
        self.manager = pygame_gui.UIManager(
            self.screen.get_size(), root / "assets" / "style.json"
        )
        self.zombie = Zombie(self.screen)
        width, height = self.screen.get_width(), self.screen.get_height()
        self.background = pg.transform.scale(
            pg.image.load(root / "assets" / "back.png").convert_alpha(),
            (width, height),
        )
        self.stats_label = UILabel(
            pg.Rect((width - 230) // 2, height * 0.05, 230, 80),
            "Statistics",
            self.manager,
        )
        self.back = UIButton(
            pg.Rect(width * 0.05, height * 0.075, 50, 50),
            "X",
            self.manager,
        )
        self.stats = UITextBox(
            "1 level:<br>    Kills: 1023<br>    Damage: 800",
            pg.Rect(
                width * 0.2,
                height * 0.3,
                width * 0.6,
                height * 0.5,
            ),
            self.manager,
        )

    def on_event(self, events) -> None:
        for event in events:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back:
                    self._context.scene = WelcomeScene(self._context)
            self.manager.process_events(event)

    def render(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.zombie.group.draw(self.screen)
        self.manager.draw_ui(self.screen)
        pg.display.flip()

    def update(self, dt: float) -> None:
        self.zombie.group.update(dt)
        self.manager.update(0)
