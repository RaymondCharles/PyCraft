from dataclasses import dataclass
from typing import Tuple

# Stores the settings and constants for the game (using dataclasses keeps related values together)
@dataclass
class GameSettings:
    world_size: int = 10
    reach_distance: int = 6
    ground_block_y: float = -0.5

    player_start_position: Tuple[float, float, float] = (0, 0, -6)
    player_speed: float = 5
    player_jump_height: float = 1.5
    player_gravity: float = 1

    fullscreen: bool  = False
    show_fps: bool = True

    