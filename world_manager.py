import json

from dataclasses import dataclass
from pathlib import Path
from typing import List

# Stores basic information about a saved world
@dataclass
class WorldInfo:
    world_id: str
    world_name: str
    save_file_path: str

# Handles creating, listing and deleting world save files
class WorldManager:
    def __init__(self, saves_folder: str):
        self.saves_folder = Path(saves_folder)
        self.saves_folder.mkdir(parents=True, exist_ok=True)

    # Finds All saved worlds
    def list_worlds(self) -> List[WorldInfo]:
        worlds = []

        for save_file in sorted(self.saves_folder.glob("*.json")):
            world_name = self.get_world_name_from_file(save_file)

            worlds.append(
                WorldInfo(
                    world_id=save_file.stem,
                    world_name=world_name,
                    save_file_path=str(save_file),
                )
            )
        
        return worlds
    
    # Creates the information for a new world save file
    def create_world_info(self) -> WorldInfo:
        world_number = 1

        while True:
            world_id = f"world_{world_number}"
            save_file_path = self.saves_folder / f"{world_id}.json"

            if not save_file_path.exists():
                break

            world_number += 1
        
        return WorldInfo(
            world_id=world_id,
            world_name=f"World {world_number}",
            save_file_path=str(save_file_path),
        )
    
    # Deletes a world save file
    def delete_world(self, save_file_path: str) -> None:
        path = Path(save_file_path)

        if path.exists() and path.parent == self.saves_folder:
            path.unlink()

    # Reads the world name from the save file
    def get_world_name_from_file(self, save_file: Path) -> str:
        try:
            with save_file.open("r", encoding="utf-8") as file:
                save_data = json.load(file)
            
            return save_data.get("world_name", save_file.stem.replace("_", " ").title())
        except json.JSONDecodeError:
            return save_file.stem.replace("_", " ").title()
