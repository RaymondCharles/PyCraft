from ursina import Ursina, destroy, window

from game_world import GameWorld
from menus import MainMenu, PauseMenu, SettingsMenu, WorldMenu
from settings import GameSettings
from world_manager import WorldManager


class PyCraftApp:
    # Controls the overall application
    def __init__(self):
        self.settings = GameSettings()
        self.world_manager = WorldManager(self.settings.saves_folder)

        self.game_world = None
        self.current_save_file_path = None

        self.main_menu = MainMenu(
            on_start=self.show_world_menu,
            on_settings=self.show_settings_menu,
        )

        self.world_menu = WorldMenu(
            world_manager=self.world_manager,
            on_create_world=self.create_new_world,
            on_load_world=self.load_world,
            on_delete_world=self.delete_world,
            on_back=self.show_main_menu,
        )

        self.settings_menu = SettingsMenu(
            settings=self.settings,
            on_back=self.show_main_menu,
        )

        self.pause_menu = PauseMenu(
            on_resume=self.resume_game,
            on_save_and_quit=self.save_and_quit_to_menu,
        )

        self.show_main_menu()

    # Hides every menu
    def hide_all_menus(self) -> None:
        self.main_menu.hide()
        self.world_menu.hide()
        self.settings_menu.hide()
        self.pause_menu.hide()

    # Shows the main menu
    def show_main_menu(self) -> None:
        self.hide_all_menus()
        self.main_menu.show()

    # Shows the world menu
    def show_world_menu(self) -> None:
        self.hide_all_menus()
        self.world_menu.show()

    # Shows the settings menu
    def show_settings_menu(self) -> None:
        self.hide_all_menus()
        self.settings_menu.show()

    # Creates and starts a new world
    def create_new_world(self) -> None:
        world_info = self.world_manager.create_world_info()
        self.start_game(world_info.save_file_path)

    # Loads an existing world
    def load_world(self, save_file_path: str) -> None:
        self.start_game(save_file_path)

    # Deletes a saved world
    def delete_world(self, save_file_path: str) -> None:
        self.world_manager.delete_world(save_file_path)

    # Starts the game world
    def start_game(self, save_file_path: str) -> None:
        self.hide_all_menus()

        if self.game_world is not None:
            destroy(self.game_world)

        self.current_save_file_path = save_file_path

        self.game_world = GameWorld(
            settings=self.settings,
            on_pause_requested=self.pause_game,
            save_file_path=save_file_path,
        )

    # Pauses the game and opens the pause menu
    def pause_game(self) -> None:
        if self.game_world is None:
            return

        self.game_world.pause()
        self.pause_menu.show()

    # Closes the pause menu and resumes gameplay
    def resume_game(self) -> None:
        self.pause_menu.hide()

        if self.game_world is not None:
            self.game_world.resume()

    # Saves the current world, destroys it, then returns to the world menu
    def save_and_quit_to_menu(self) -> None:
        if self.game_world is not None:
            self.game_world.save_world()
            self.game_world.destroy_world()
            self.game_world = None

        self.current_save_file_path = None
        self.show_world_menu()


app = Ursina()

window.title = "PyCraft"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

pycraft = PyCraftApp()

app.run()