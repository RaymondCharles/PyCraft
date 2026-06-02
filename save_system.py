import json

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


Vector3Tuple = Tuple[float, float, float]

# Stores loaded save data into clean python object. This makes the rest of the game code easier to read than passing raw dictionaries around everywhere.
@dataclass
class WorldSaveData:
    player_position: Vector3Tuple
    blocks: List[Dict[str, Any]]

#  Handles saving and loading the world. The world is saved as a JSON file, which is easy to read and debug.
class SaveSystem:
    def __init__(self, save_file_path: str):
        self.save_file_path = Path(save_file_path)

    # Saves the player's position and all blocks in the world
    def save_world(self, player_position, blocks) -> None:
        self.save_file_path.parent.mkdir(parents=True, exist_ok=True)

        save_data = {
            "player_position": list(self.vector_to_tuple(player_position)),
            "blocks": [],
        }

        for block in blocks:
            block_data = {
                "position": list(self.vector_to_tuple(block.position)),
                "block_type": block.block_type,
            }

            save_data["blocks"].append(block_data)

        with self.save_file_path.open("w", encoding="utf-8") as save_file:
            json.dump(save_data, save_file, indent=4)

    # Loads the world if a save file exists. If there is no save file yet, this returns None
    def load_world(self) -> Optional[WorldSaveData]:
        if not self.save_file_path.exists():
            return None

        with self.save_file_path.open("r", encoding="utf-8") as save_file:
            raw_data = json.load(save_file)

        player_position = tuple(raw_data.get("player_position", (0, 0, -6)))
        blocks = raw_data.get("blocks", [])

        return WorldSaveData(
            player_position=player_position,
            blocks=blocks,
        )
        
      
   #Converts Ursina Vec3 values into normal Python tuples.
   #JSON cannot directly save Ursina's Vec3 type, so we convert: Vec3(1, 2, 3) -> (1, 2, 3)
    @staticmethod
    def vector_to_tuple(value) -> Vector3Tuple:
        x = getattr(value, "x", value[0])
        y = getattr(value, "y", value[1])
        z = getattr(value, "z", value[2])

        return (
            round(float(x), 2),
            round(float(y), 2),
            round(float(z), 2),
        )