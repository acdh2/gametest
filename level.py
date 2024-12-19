from game import *
from box import *
from player import *
import random

# Define constants
tileSize = 32

class Level(GameObject):
    def __init__(self, collisionManager):
        super().__init__()
        self.collisionManager = collisionManager
        self.updatables = []

    def loadLevel(self, levelData):
        self.clearLevel()  # Ensure any existing tiles are removed
        """Load level and register collidable tiles."""
        tileSize = 32
        for rowIndex, row in enumerate(levelData):
            for colIndex, cell in enumerate(row):
                if cell == 1:  # Tile
                    tile = Sprite("assets/tile.png", x=colIndex * tileSize, y=rowIndex * tileSize)
                    self.addChild(tile)
                    self.collisionManager.add(tile)  # Register tile with CollisionManager
                if cell == 2:
                    box = Box(self.collisionManager, x=colIndex * tileSize, y=rowIndex * tileSize)
                    self.addChild(box)
                    self.collisionManager.add(box)  # Register tile with CollisionManager
                    self.updatables.append(box)
                if cell == 3:
                    self.player = Player(self.collisionManager, x=colIndex * tileSize, y=rowIndex * tileSize)
                    self.addChild(self.player)                    
                    self.collisionManager.add(self.player)  # Register tile with CollisionManager
                    self.updatables.append(self.player)

    def clearLevel(self):
        """Clear the current level by removing all tiles."""
        self.removeAllChildren()  # Use the GameObject's removeAllChildren method
        
    def update(self):
        for updatable in self.updatables:
            updatable.update()

    def setup(self):
        """Setup the level by loading it."""
        # Create a 20x15 grid with mostly zeros and a few random ones
        levelData = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 3, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.loadLevel(levelData)