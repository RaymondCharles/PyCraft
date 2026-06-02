from ursina import Entity, color

# Different block types can have different colours
block_colours = {
    "grass": color.rgb(0, 220, 0),
    "red": color.red,
}

# Represents one block in the world -> inherits from Entity Class (Entity being any object in game world)
class Block(Entity):
    def __init__(self, position, block_type: str = "grass", parent=None):
        self.block_type = block_type

        super().__init__(
            parent=parent,
            model="cube",
            position=position,
            scale=1,
            color=block_colours.get(block_type, color.white),
            texture="white_cube",
            collider="box"
        )
