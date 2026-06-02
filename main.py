from ursina import Ursina, destroy, window

from game_world import GameWorld
from menus import MainMenu, PauseMenu, SettingsMenu
from settings import GameSettings


class PyCraftApp:
    """
    Controls the overall application.

    This class decides whether the player is:
    - in the main menu
    - in the settings menu
    - inside the game world
    - inside the pause menu
    """

    def __init__(self):
        self.settings = GameSettings()
        self.game_world = None

        self.main_menu = MainMenu(
            on_start=self.start_game,
            on_settings=self.show_settings_menu,
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
        self.settings_menu.hide()
        self.pause_menu.hide()
    
    # Shows the main menu
    def show_main_menu(self) -> None:
        self.hide_all_menus()
        self.main_menu.show()

    # Shows the settings menu    
    def show_settings_menu(self) -> None:
        self.hide_all_menus()
        self.settings_menu.show()

    # Starts a new game world.
    def start_game(self) -> None:
        self.hide_all_menus()

        if self.game_world is not None:
            destroy(self.game_world)

        self.game_world = GameWorld(
            settings=self.settings,
            on_pause_requested=self.pause_game,
        )

    # Pauses the game and opens the pause menu.
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

    # Returns to main menu
    def save_and_quit_to_menu(self) -> None:
        if self.game_world is not None:
            self.game_world.save_world()
            self.game_world.destroy_world()
            self.game_world = None

        self.show_main_menu()


app = Ursina()

window.title = "PyCraft"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

pycraft = PyCraftApp()

app.run()