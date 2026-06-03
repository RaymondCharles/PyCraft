from dataclasses import dataclass
from typing import Tuple

# Stores the settings and constants for the game (using dataclasses keeps related values together)
@dataclass
class GameSettings:
    # World Settings
    world_size: int = 10
    reach_distance: int = 6
    ground_block_y: float = -0.5

    # Player Settings
    player_start_position: Tuple[float, float, float] = (0, 0, -6)
    player_speed: float = 5
    player_jump_height: float = 1.5
    player_gravity: float = 1

    # Window Settings
    fullscreen: bool  = False
    show_fps: bool = True

    # Save Settings
    saves_folder: str = "saves"