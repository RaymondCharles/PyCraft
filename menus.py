from typing import Callable

from ursina import Button, Entity, Text, application, camera, color, destroy, mouse, window

from settings import GameSettings
from world_manager import WorldManager


class BaseMenu(Entity):
    # Base class for all menus
    def __init__(self):
        super().__init__(parent=camera.ui)

        self.background = Entity(
            parent=self,
            model="quad",
            scale=(2, 1),
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


class MainMenu(BaseMenu):
    # The first menu the player sees when opening the game
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


class WorldMenu(BaseMenu):
    # Menu for creating, loading and deleting worlds
    def __init__(
        self,
        world_manager: WorldManager,
        on_create_world: Callable[[], None],
        on_load_world: Callable[[str], None],
        on_delete_world: Callable[[str], None],
        on_back: Callable[[], None],
    ):
        super().__init__()

        self.world_manager = world_manager
        self.on_create_world = on_create_world
        self.on_load_world = on_load_world
        self.on_delete_world = on_delete_world
        self.on_back = on_back
        self.world_buttons = []

        Text(
            text="Select World",
            parent=self,
            origin=(0, 0),
            position=(0, 0.32),
            scale=2.5,
        )

        Button(
            text="Create New World",
            parent=self,
            scale=(0.45, 0.07),
            position=(0, 0.18),
            color=color.azure,
            on_click=self.on_create_world,
        )

        self.no_worlds_text = Text(
            text="No saved worlds yet",
            parent=self,
            origin=(0, 0),
            position=(0, 0.04),
            scale=1.3,
            color=color.light_gray,
        )

        Button(
            text="Back",
            parent=self,
            scale=(0.35, 0.07),
            position=(0, -0.34),
            color=color.gray,
            on_click=self.on_back,
        )

        self.refresh_world_list()

    # Shows the world menu and refreshes the saved world list
    def show(self) -> None:
        self.refresh_world_list()
        super().show()

    # Clears old world buttons
    def clear_world_buttons(self) -> None:
        for button in self.world_buttons:
            destroy(button)

        self.world_buttons.clear()

    # Refreshes the saved world list
    def refresh_world_list(self) -> None:
        self.clear_world_buttons()

        worlds = self.world_manager.list_worlds()
        self.no_worlds_text.enabled = len(worlds) == 0

        start_y = 0.06

        for index, world in enumerate(worlds[:5]):
            y_position = start_y - (index * 0.1)

            load_button = Button(
                text=f"Load {world.world_name}",
                parent=self,
                scale=(0.35, 0.065),
                position=(-0.11, y_position),
                color=color.green,
                on_click=lambda path=world.save_file_path: self.on_load_world(path),
            )

            delete_button = Button(
                text="Delete",
                parent=self,
                scale=(0.16, 0.065),
                position=(0.26, y_position),
                color=color.red,
                on_click=lambda path=world.save_file_path: self.delete_world(path),
            )

            self.world_buttons.append(load_button)
            self.world_buttons.append(delete_button)

    # Deletes a world and refreshes the list
    def delete_world(self, save_file_path: str) -> None:
        self.on_delete_world(save_file_path)
        self.refresh_world_list()

    # Pressing Escape goes back to the main menu
    def input(self, key) -> None:
        if self.enabled and key == "escape":
            self.on_back()


class SettingsMenu(BaseMenu):
    # Settings menu
    def __init__(
        self,
        settings: GameSettings,
        on_back: Callable[[], None],
    ):
        super().__init__()

        self.settings = settings
        self.on_back = on_back

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

    # Updates button labels so they match the current settings
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

    # Turns the FPS counter on/off
    def toggle_fps_counter(self) -> None:
        self.settings.show_fps = not self.settings.show_fps
        window.fps_counter.enabled = self.settings.show_fps

        self.update_button_text()

    # Pressing Escape inside settings goes back to the main menu
    def input(self, key) -> None:
        if self.enabled and key == "escape":
            self.on_back()


class PauseMenu(BaseMenu):
    # Menu shown while the player is inside a world
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

    # Pressing Escape while paused resumes the game
    def input(self, key) -> None:
        if self.enabled and key == "escape":
            self.on_resume()