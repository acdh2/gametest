from game import *
        
class Player(AnimSprite):
    def __init__(self, collisionManager, x=0, y=0, rotation=0, scaleX=1, scaleY=1):
        super().__init__("assets/player.png", 1, 1, x, y, rotation, scaleX, scaleY)
        self.collisionManager = collisionManager

        self.velocity = Vector2()        
        self.landed = False

    def moveStep(self, dx, dy):
        """Move the player and resolve collisions."""
        self.x += dx
        self.y += dy
        collision = self.collisionManager.checkCollision(self, Vector2(dx, dy))
        if collision:
            # Handle collision (e.g., stop movement)
            self.x -= dx
            self.y -= dy
            return False
        return True

    def move(self, dx, dy):
        # Calculate the length of the vector
        length = int((dx**2 + dy**2)**0.5)
        
        if length > 0:
            # Calculate the step increments
            stepX = dx / length
            stepY = dy / length
    
            for _ in range(length):
                if not self.moveStep(stepX, stepY):
                    # Collision occurred; stop further movement
                    return False
            
        return True
        
    def shouldCollide(self, other, impact):
        #if (other.y >= self.y + self.height - 8 and impact.y < 0):
        #    return True
        #return False
        return True
        
    def update(self):
#        if Input.getKey("s"):
#            self.move(0, 3)
            
        if not self.move(0, self.velocity.y):
            if self.velocity.y > 0:
                self.landed = True
            self.velocity.y = 0
        else:
            self.velocity.y += 1
            
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
        
        if self.y > 600:
            self.y = 0
            self.velocity.y = 0