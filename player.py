from box import *
        
class Player(Box):
    def __init__(self, collisionManager, x=0, y=0, rotation=0, scaleX=1, scaleY=1):
        super().__init__(collisionManager, x, y, rotation, scaleX, scaleY)

    def update(self):
            
        self.updatePhysics()
                    
        if self.landed:
            if Input.getKey("space"):
                self.landed = False
                self.velocity.y = -16
            
        if not Input.getKey("space"):
            if self.velocity.y < 0:
                self.velocity.y *= 0.9
        
        if Input.getKey("a"):
            self.move(-5, 0)
        if Input.getKey("d"):
            self.move(5, 0)

    def shouldCollide(self, other, impact):
        return True
