from ursina import Entity, color

# Represents one block in the world -> inherits from Entity Class (Entity being any object in game world)
class Block(Entity):
    def __init__(self, position, block_color=color.green, parent=None):
        super().__init__(
            parent=parent,
            model="cube",
            position=position,
            scale=1,
            color=block_color,
            texture="white_cube",
            collider="box"
        )
