from typing import Callable, Dict, Tuple

from ursina import (
    BoxCollider,
    Entity,
    Sky,
    Vec3,
    camera,
    color,
    destroy,
    mouse,
    raycast,
)

from ursina.prefabs.first_person_controller import FirstPersonController

from block import Block
from settings import GameSettings

BlockPosition = Tuple[float, float, float]

# Controls the actual playable world, so handles creating blocks, player, breaking/placing blocks, spawning and resuming gameplay
class GameWorld(Entity):
    def __init__(
            self,
            settings: GameSettings,
            on_pause_requested: Callable[[], None],
    ):
        super().__init__()

        self.settings = settings
        self.on_pause_requested = on_pause_requested

        self.blocks: Dict[BlockPosition, Block] = {}
        self.player = None
        self.sky = None
        self.is_paused = None

        self.create_flat_world()
        self.create_test_block()
        self.create_player()
        self.create_sky()

        self.resume()

    # Converts block position into clean dictionary key for save/load
    def position_to_key(self, position) -> BlockPosition:
        x = getattr(position, "x", position[0])
        y = getattr(position, "y", position[1])
        z = getattr(position, "z", position[2])

        return (
            round(float(x), 2),
            round(float(y), 2),
            round(float(z), 2),
        )
    
    # Creates blcok and stores it in blocks dictionary
    def add_block(self, position, block_color=color.green) -> Block:
        block = Block(
            position=position,
            block_color=block_color,
            parent=self,
        )

        block_key = self.position_to_key(block.position)
        self.blocks[block_key] = block

        return block
    # Removes blcok from the world and from the blocks dictionary
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
                    block_color=color.rgb(0, 220, 0),
                )
    
    # Test block
    def create_test_block(self) -> None:
        self.add_block(
            position=(0, 0.5, 5),
            block_color=color.red,
        )
    
    # Creates fps controller
    def create_player(self) -> None:
        self.player = FirstPersonController(
            position = self.settings.player_start_position,
            speed=self.settings.player_speed,
            jump_height=self.settings.player_jump_height,
            gravity=self.settings.player_gravity,
            origin_y=-0.5
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
        
        self.handle_block_interation(key)
    
    # Handles block breaking/placing
    def handle_block_interation(self, key) -> None:
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
            self.remove_block(hit_info, Block)
            return
        
        if key == "right mouse down":
            new_block_position = hit_info.entity.position + hit_info.normal
            block_key = self.position_to_key(new_block_position)

            if block_key in self.blocks:
                return
            
            self.add_block(
                position=new_block_position,
                block_color=color.red,
            )