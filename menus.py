from typing import Callable
from ursina import Button, Entity, Text, application, camera, color, mouse, window
from settings import GameSettings

# Base class for all menus
class BaseMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)

        self.background = Entity(
            parent=self,
            model="quad",
            scale=(2,1),
            color=color.rgba(0, 0, 0, 180),
            z=1,
        )

        self.enabled = False

    # Shows the menu and unlocks the mouse
    def show(self) -> None:
        self.enabled = True
        mouse.locked = False
        mouse.visible = True

    # Hides the menu
    def hide(self) -> None:
        self.enabled = False

# First menu the player sees when opening the game
class MainMenu(BaseMenu):
    def __init__(
            self,
            on_start: Callable[[], None],
            on_settings: Callable[[], None],
    ):
        super().__init__()

        Text(
            text="PyCraft",
            parent=self,
            origin=(0, 0),
            position=(0, 0.28),
            scale=3,
        )

        Button(
            text="Start Game",
            parent=self,
            scale=(0.35, 0.08),
            position=(0, 0.08),
            color=color.azure,
            on_click=on_start,
        )

        Button(
            text="Settings",
            parent=self,
            scale=(0.35, 0.08),
            position=(0, -0.04),
            color=color.orange,
            on_click=on_settings,
        )

        Button(
            text="Leave Game",
            parent=self,
            scale=(0.35, 0.08),
            position=(0, -0.16),
            color=color.red,
            on_click=application.quit,
        )

# Settings Menu -> Fullscreen on/off, FPS counter on/off (for now atleast)
class SettingsMenu(BaseMenu):
    def __init__(
            self,
            settings: GameSettings,
            on_back: Callable[[], None],
    ):
        super().__init__()

        self.settings = settings

        Text(
            text="Settings",
            parent=self,
            origin=(0, 0),
            position=(0, 0.28),
            scale=2.5,
        )

        self.fullscreen_button = Button(
            parent=self,
            scale=(0.45, 0.08),
            position=(0, 0.08),
            color=color.azure,
            on_click=self.toggle_fullscreen,
        )

        self.fps_button = Button(
            parent=self,
            scale=(0.45, 0.08),
            position=(0, -0.04),
            color=color.orange,
            on_click=self.toggle_fps_counter,
        )

        Button(
            text="Back",
            parent=self,
            scale=(0.35, 0.08),
            position=(0, -0.18),
            color=color.gray,
            on_click=on_back,
        )

        self.update_button_text()
    
    # Update button labels so they match the current settings
    def update_button_text(self) -> None:
        fullscreen_text = "ON" if self.settings.fullscreen else "OFF"
        fps_text = "ON" if self.settings.show_fps else "OFF"

        self.fullscreen_button.text = f"Fullscreen: {fullscreen_text}"
        self.fps_button.text = f"FPS Counter: {fps_text}"

    # Turns fullscreen on/off
    def toggle_fullscreen(self) -> None:
        self.settings.fullscreen = not self.settings.fullscreen
        window.fullscreen = self.settings.fullscreen

        self.update_button_text()

    # Turns FPS Counter on/off
    def toggle_fps_counter(self) -> None:
        self.settings.show_fps = not self.settings.show_fps
        window.fps_counter.enabled = self.settings.show_fps

        self.update_button_text()
    
    # Pressing Escape inside settings goes back to main menu
    def input(self, key) -> None:
        if self.enabled and key == "escape":
            self.hide()

# Menu shown while player is inside of a world
class PauseMenu(BaseMenu):
    def __init__(
        self,
        on_resume: Callable[[], None],
        on_save_and_quit: Callable[[], None],
    ):
        super().__init__()

        self.on_resume = on_resume

        Text(
            text="Game Paused",
            parent=self,
            origin=(0, 0),
            position=(0, 0.28),
            scale=2.5,
        )

        Button(
            text="Resume Game",
            parent=self,
            scale=(0.4, 0.08),
            position=(0, 0.08),
            color=color.azure,
            on_click=on_resume,
        )

        Button(
            text="Save & Quit to Menu",
            parent=self,
            scale=(0.4, 0.08),
            position=(0, -0.04),
            color=color.orange,
            on_click=on_save_and_quit,
        )

        Button(
            text="Quit Application",
            parent=self,
            scale=(0.4, 0.08),
            position=(0, -0.16),
            color=color.red,
            on_click=application.quit,
        )
    # Pressing escape while paused resumes the game.    
    def input(self, key) -> None:
        if self.enabled and key == "escape":
            self.on_resume()