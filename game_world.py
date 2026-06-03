from typing import Callable, Dict, Tuple

from ursina import (
    BoxCollider,
    Entity,
    Sky,
    Vec3,
    camera,
    destroy,
    mouse,
    raycast,
)

from ursina.prefabs.first_person_controller import FirstPersonController

from block import Block
from save_system import SaveSystem, WorldSaveData
from settings import GameSettings


BlockPosition = Tuple[float, float, float]


# Controls the actual playable world, so handles creating blocks, player, breaking/placing blocks, saving/loading world, spawning and resuming gameplay
class GameWorld(Entity):
    def __init__(
        self,
        settings: GameSettings,
        on_pause_requested: Callable[[], None],
        save_file_path: str,
    ):
        super().__init__()

        self.settings = settings
        self.on_pause_requested = on_pause_requested
        self.save_system = SaveSystem(save_file_path)

        self.blocks: Dict[BlockPosition, Block] = {}
        self.player = None
        self.sky = None
        self.is_paused = False

        save_data = self.save_system.load_world()

        if save_data is None:
            self.create_flat_world()
            self.create_test_block()
            player_position = self.settings.player_start_position
        else:
            self.load_blocks_from_save(save_data)
            player_position = self.get_safe_player_position(save_data.player_position)

        self.ensure_spawn_area_is_safe()
        self.create_world_borders()
        self.create_safety_floor()
        self.create_player(player_position)
        self.create_sky()

        self.resume()

    # Converts block position into clean dictionary key for save/load
    def position_to_key(self, position) -> BlockPosition:
        if hasattr(position, "x"):
            x = position.x
            y = position.y
            z = position.z
        else:
            x = position[0]
            y = position[1]
            z = position[2]

        return (
            round(float(x), 2),
            round(float(y), 2),
            round(float(z), 2),
        )

    # Converts player position into nearest ground block key
    def get_ground_key_under_position(self, position) -> BlockPosition:
        if hasattr(position, "x"):
            x = position.x
            z = position.z
        else:
            x = position[0]
            z = position[2]

        return (
            round(float(round(x)), 2),
            round(float(self.settings.ground_block_y), 2),
            round(float(round(z)), 2),
        )

    # Checks if a position is inside the playable map area
    def is_inside_world_boundaries(self, position) -> bool:
        if hasattr(position, "x"):
            x = position.x
            z = position.z
        else:
            x = position[0]
            z = position[2]

        border_limit = self.settings.world_size - 0.5

        return abs(x) <= border_limit and abs(z) <= border_limit

    # Checks if there is a ground block under a position
    def has_ground_under_position(self, position) -> bool:
        ground_key = self.get_ground_key_under_position(position)
        return ground_key in self.blocks

    # Makes sure the default spawn position always has a ground block underneath it
    def ensure_spawn_area_is_safe(self) -> None:
        spawn_ground_key = self.get_ground_key_under_position(
            self.settings.player_start_position
        )

        if spawn_ground_key not in self.blocks:
            self.add_block(
                position=spawn_ground_key,
                block_type="grass",
            )

    # Checks if saved player position is safe, otherwise resets player back to spawn point
    def get_safe_player_position(self, position):
        if hasattr(position, "y"):
            y = position.y
        else:
            y = position[1]

        if y < -0.25:
            return self.settings.player_start_position

        if not self.is_inside_world_boundaries(position):
            return self.settings.player_start_position

        if not self.has_ground_under_position(position):
            return self.settings.player_start_position

        return position

    # Creates block and stores it in blocks dictionary
    def add_block(self, position, block_type: str = "grass") -> Block:
        block = Block(
            position=position,
            block_type=block_type,
            parent=self,
        )

        block_key = self.position_to_key(block.position)
        self.blocks[block_key] = block

        return block

    # Removes block from the world and from the blocks dictionary
    def remove_block(self, block: Block) -> None:
        block_key = self.position_to_key(block.position)
        self.blocks.pop(block_key, None)

        destroy(block)

    # Creates a flat world made of individual cube blocks
    def create_flat_world(self) -> None:
        for x in range(-self.settings.world_size, self.settings.world_size + 1):
            for z in range(-self.settings.world_size, self.settings.world_size + 1):
                self.add_block(
                    position=(x, self.settings.ground_block_y, z),
                    block_type="grass",
                )

    # Test block
    def create_test_block(self) -> None:
        self.add_block(
            position=(0, 0.5, 5),
            block_type="red",
        )

    # Recreates blocks from the save file
    def load_blocks_from_save(self, save_data: WorldSaveData) -> None:
        for block_data in save_data.blocks:
            position = tuple(block_data["position"])
            block_type = block_data.get("block_type", "grass")

            self.add_block(
                position=position,
                block_type=block_type,
            )

    # Creates world boundary system
    def create_world_borders(self) -> None:
        # We are not using physical invisible wall colliders anymore.
        # Physical walls caused the player to sometimes get stuck.
        # The update method below keeps the player inside the map instead.
        pass

    # Creates safety floor system
    def create_safety_floor(self) -> None:
        # We are not using a physical invisible safety floor anymore.
        # A physical floor under the map caused the player to get trapped under the blocks.
        # The update method below resets the player if they fall below the map.
        pass

    # Creates fps controller
    def create_player(self, position) -> None:
        self.player = FirstPersonController(
            position=position,
            speed=self.settings.player_speed,
            jump_height=self.settings.player_jump_height,
            gravity=self.settings.player_gravity,
            origin_y=-0.5,
        )

        self.player.parent = self

        self.player.collider = BoxCollider(
            self.player,
            center=Vec3(0, 1, 0),
            size=Vec3(1, 2, 1),
        )

    # Sky - Adds Sky background to the world
    def create_sky(self) -> None:
        self.sky = Sky()
        self.sky.parent = self

    # Locks/Unlocks Mouse during gameplay
    def set_mouse_lock(self, is_locked: bool) -> None:
        mouse.locked = is_locked
        mouse.visible = not is_locked

    # Pause the game
    def pause(self) -> None:
        self.is_paused = True
        self.set_mouse_lock(False)

        if self.player is not None:
            self.player.enabled = False

    # Resume the game
    def resume(self) -> None:
        self.is_paused = False
        self.set_mouse_lock(True)

        if self.player is not None:
            self.player.enabled = True

    # Resets the player back to a safe spawn position
    def reset_player_to_spawn(self) -> None:
        if self.player is None:
            return

        self.ensure_spawn_area_is_safe()
        self.player.position = self.settings.player_start_position

        if hasattr(self.player, "air_time"):
            self.player.air_time = 0

    # Runs every frame and keeps the player inside the map boundaries
    def update(self) -> None:
        if self.player is None or self.is_paused:
            return

        border_limit = self.settings.world_size - 0.5

        self.player.x = max(-border_limit, min(border_limit, self.player.x))
        self.player.z = max(-border_limit, min(border_limit, self.player.z))

        if self.player.y < -0.25:
            self.reset_player_to_spawn()

    # Saves the current state of the world.
    def save_world(self) -> None:
        if self.player is None:
            return

        safe_player_position = self.get_safe_player_position(self.player.position)

        self.save_system.save_world(
            player_position=safe_player_position,
            blocks=self.blocks.values(),
        )

    # Destroys the current world but saves it
    def destroy_world(self) -> None:
        self.pause()
        destroy(self)

    # Handles gameplay input
    def input(self, key) -> None:
        if self.is_paused:
            return

        if key == "escape":
            self.on_pause_requested()
            return

        if key not in ("left mouse down", "right mouse down"):
            return

        self.handle_block_interaction(key)

    # Handles block breaking/placing
    def handle_block_interaction(self, key) -> None:
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.settings.reach_distance,
            ignore=[self.player],
        )

        if not hit_info.hit:
            return

        if not isinstance(hit_info.entity, Block):
            return

        if key == "left mouse down":
            self.remove_block(hit_info.entity)
            return

        if key == "right mouse down":
            new_block_position = hit_info.entity.position + hit_info.normal
            block_key = self.position_to_key(new_block_position)

            if block_key in self.blocks:
                return

            self.add_block(
                position=new_block_position,
                block_type="red",
            )