from abc import ABC, abstractmethod
from os import getcwd
from pathlib import Path

import pygame
import pygame_gui

# "#2f353b"
pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Greeting")
root = Path(getcwd())
background = pygame.transform.scale(
    pygame.image.load(root / "assets" / "back.png").convert_alpha(), (width, height)
)
running = True
clock = pygame.time.Clock()
manager = pygame_gui.UIManager(size, root / "assets" / "style.json")
animation = pygame.sprite.GroupSingle()


class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(animation)
        self.width, self.height = 111, 162
        self.images = [
            pygame.transform.scale(
                pygame.image.load(
                    root / "assets" / "zombie" / f"{i}.png"
                ).convert_alpha(),
                (self.width, self.height),
            )
            for i in range(5)
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = width - self.width
        self.rect.y = height - self.height
        self.v = 30
        self.x = width - self.width
        self.k_rotates = 0
        self.rotate = False
        self.left = True
        self.animation_rate = 0

    def update(self, dt):
        self.x -= self.v * dt
        self.rect.x = self.x
        self.animation_rate += 3 * dt
        if not 0 < self.x <= width - self.width and not self.rotate:
            self.v = 0
            self.rotate = True
            self.k_rotates = self.animation_rate
        if not self.rotate:
            self.image = self.images[int(self.animation_rate) % 2]
        else:
            if self.animation_rate - self.k_rotates < 3:
                self.image = self.images[2 + int(self.animation_rate - self.k_rotates)]
            else:
                for i in range(5):
                    self.images[i] = pygame.transform.flip(self.images[i], True, False)
                self.v = -30 if self.left else 30
                self.x += 2 if self.left else -2
                self.left = not self.left
                self.k_rotates = 0
                self.rotate = False


class AbstractScene(ABC):
    def __init__(self, context: "SceneContext") -> None:
        self._context = context

    @abstractmethod
    def on_click(self, event) -> None:
        pass


class SceneContext:
    def __init__(self) -> None:
        self._scene = WelcomeScene()
        self.zombie = Zombie()

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, value):
        self._scene = value

    def handler(self, event):
        self._scene.on_click(event)

    def move_animation(self):
        animation.draw(screen)
        animation.update(clock.tick() / 1000)

    def render(self):
        screen.blit(background, (0, 0))
        self.move_animation()
        manager.update(0)
        manager.draw_ui(screen)


class WelcomeScene:
    def __init__(self) -> None:
        self.poom_label = pygame_gui.elements.UILabel(
            pygame.Rect((width - 220) // 2, height * 0.05, 220, 110),
            "Poom",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#poom"),
        )
        self.play = pygame_gui.elements.UIButton(
            pygame.Rect((width - 160) // 2, height * 0.3, 160, 70),
            "Play",
            manager,
        )
        self.settings = pygame_gui.elements.UIButton(
            pygame.Rect((width - 160) // 2, height * 0.4, 160, 70),
            "Settings",
            manager,
        )
        self.statistics = pygame_gui.elements.UIButton(
            pygame.Rect((width - 160) // 2, height * 0.5, 160, 70),
            "Statistics",
            manager,
        )
        self.quit = pygame_gui.elements.UIButton(
            pygame.Rect((width - 160) // 2, height * 0.6, 160, 70),
            "Quit",
            manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            manager.clear_and_reset()
            if event.ui_element == self.play:
                print("play")
            if event.ui_element == self.settings:
                sc.scene = SettingsScene()
            if event.ui_element == self.statistics:
                sc.scene = StatiscticsScene()
            if event.ui_element == self.quit:
                print("quit")


class SettingsScene:
    def __init__(self) -> None:
        self.settings_label = pygame_gui.elements.UILabel(
            pygame.Rect((width - 230) // 2, height * 0.05, 230, 80),
            "Settings",
            manager,
        )
        self.back = pygame_gui.elements.UIButton(
            pygame.Rect(width * 0.05, height * 0.075, 50, 50),
            "X",
            manager,
        )
        self.graphics_lbl = pygame_gui.elements.UILabel(
            pygame.Rect((width - 200) // 2, height * 0.23, 100, 50),
            "Quality:",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#sublabel"),
        )
        self.graphics = pygame_gui.elements.UIDropDownMenu(
            ["Low", "Medium", "High"],
            "Low",
            pygame.Rect((width - 200) // 2, height * 0.3, 200, 50),
            manager,
        )
        self.screen_size_lbl = pygame_gui.elements.UILabel(
            pygame.Rect((width - 200) // 2, height * 0.4, 150, 50),
            "Screen size:",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#sublabel"),
        )
        self.screen_size = pygame_gui.elements.UIDropDownMenu(
            ["800x600 (4:3)", "1024x768 (4:3)", "1280x720 (16:9)"],
            "800x600 (4:3)",
            pygame.Rect((width - 200) // 2, height * 0.47, 290, 50),
            manager,
        )
        self.volume_lbl = pygame_gui.elements.UILabel(
            pygame.Rect((width - 200) // 2, height * 0.58, 100, 50),
            "Volume:",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#sublabel"),
        )
        self.volume = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((width - 200) // 2, height * 0.65, 270, 30),
            0.5,
            range(101),
            manager,
        )
        self.current_volume = pygame_gui.elements.UILabel(
            pygame.Rect(width * 0.7, height * 0.635, 100, 50),
            "50 %",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#sublabel"),
        )
        self.fps_lbl = pygame_gui.elements.UILabel(
            pygame.Rect((width - 200) // 2, height * 0.71, 100, 50),
            "Fps tick:",
            manager,
            object_id=pygame_gui.core.ui_element.ObjectID(object_id="#sublabel"),
        )
        self.fps = pygame_gui.elements.UIDropDownMenu(
            ["on", "off"],
            "off",
            pygame.Rect((width - 200) // 2, height * 0.78, 150, 50),
            manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self.current_volume.set_text(f"{int(self.volume.current_value * 100)} %")
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back:
                manager.clear_and_reset()
                sc.scene = WelcomeScene()


class StatiscticsScene:
    def __init__(self) -> None:
        self.stats_label = pygame_gui.elements.UILabel(
            pygame.Rect((width - 230) // 2, height * 0.05, 230, 80),
            "Statistics",
            manager,
        )
        self.back = pygame_gui.elements.UIButton(
            pygame.Rect(width * 0.05, height * 0.075, 50, 50),
            "X",
            manager,
        )
        self.stats = pygame_gui.elements.UITextBox(
            "1 level:<br>    Kills: 1023<br>    Damage: 800",
            pygame.Rect(width * 0.2, height * 0.3, width * 0.6, height * 0.5),
            manager,
        )

    def on_click(self, event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back:
                manager.clear_and_reset()
                sc.scene = WelcomeScene()


sc = SceneContext()

pygame.mixer.init()
pygame.mixer.music.load(root / "assets" / "main.mp3")
pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.WINDOWMINIMIZED:
            pygame.mixer.music.pause()
        if event.type == pygame.WINDOWRESTORED:
            pygame.mixer.music.unpause()
        sc.handler(event)
        manager.process_events(event)
    sc.render()

    pygame.display.update()
