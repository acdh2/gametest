from game import *
        
class Box(AnimSprite):
    def __init__(self, collisionManager, x=0, y=0, rotation=0, scaleX=1, scaleY=1):
        super().__init__("assets/player.png", 1, 1, x, y, rotation, scaleX, scaleY)
        self.collisionManager = collisionManager

        self.velocity = Vector2()        
        self.landed = False

    def moveStep(self, dx, dy):
        """Move the player and resolve collisions."""
        previousX = self.x
        previousY = self.y
        self.x += dx
        self.y += dy
        collision = self.collisionManager.checkCollision(self, Vector2(dx, dy))
        if collision:
            # Handle collision (e.g., stop movement)
            self.x = previousX
            self.y = previousY
            return False
        return True

    def move(self, dx, dy):
        dx = int(dx)
        dy = int(dy)
        length = int(dx * dx + dy * dy)
    
        if length > 0:
            if dx != 0 and dy != 0:
                if not self.move(dx, 0):
                    return False
                dx = 0
            
            stepX = int(dx / abs(dx)) if dx != 0 else 0  # Step direction in x (±1 or 0)
            stepY = int(dy / abs(dy)) if dy != 0 else 0  # Step direction in y (±1 or 0)
    
            for _ in range(abs(dx) if dx != 0 else abs(dy)):
                if not self.moveStep(stepX, stepY):
                    return False

        return True
        
    def updateBoundaries(self):
        if self.y > self.game.height:
            self.teleport(self.x, self.y - self.game.height)
            self.velocity.y = 0
            
        # Wrap the x position using self.teleport
        if self.x < 0:
            self.teleport(self.game.width, self.y)
        elif self.x > self.game.width:
            self.teleport(0, self.y)            
                
    def updatePhysics(self):
        if not self.move(0, self.velocity.y):
            if self.velocity.y > 0:
                self.landed = True
            self.velocity.y = 0
        else:
            self.velocity.y += 1
                    

        self.updateBoundaries()
        
    def teleport(self, targetX, targetY):
        """Teleport the object to a new position. If there's a collision, move it upwards until no collision is found."""
        self.x = targetX
        self.y = targetY

        while self.collisionManager.checkCollision(self, Vector2(0, 0)):
            self.y -= 1  # Move upward to resolve collision
             
    def update(self):
        self.updatePhysics()
            
    def shouldCollide(self, other, impact):
        if (impact.x != 0):
            return not self.move(impact.x, 0)
        
        return True
