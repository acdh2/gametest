from game import *
        
class Tile(AnimSprite):
    def __init__(self, collisionManager, x=0, y=0, rotation=0, scaleX=1, scaleY=1):
        super().__init__("assets/tile.png", 1, 1, x, y, rotation, scaleX, scaleY)
        self.collisionManager = collisionManager

        self.velocity = Vector2()        
        self.landed = False
        
    def shouldCollide(self, other, impact):
        if (self.y >= other.y + other.height - 1 and impact.y > 0):
            return True
        return False

