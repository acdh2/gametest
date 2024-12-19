from game import *

class MyGame(Game):
    def __init__(self):
        super().__init__(width=640, height=480, title="Game")

    """
    Game implementation that creates two sprites and rotates them.
    """
    def setup(self):
                
        """Create sprites and set up the game."""
        """Create two sprites for collision testing."""
        self.sprite1 = Sprite("texture.png", x=320, y=240, rotation=0)
        self.sprite2 = AnimSprite("colors.png", columns=2, rows=2, x=320, y=260, rotation=45, scaleX=1, scaleY=1, originX=16, originY=16 )
        
        self.addChild(self.sprite1)
        self.addChild(self.sprite2)

        self.text = Text("Hello world", x=320, y=240, rotation=0, scaleX=1, scaleY=1, originX=77, originY=0)
        
        self.addChild(self.text)    
        
        sound = Sound("snowland.ogg")
        sound.play()            
        
    def update(self):
        """Update and test for collisions."""
        self.sprite1.rotation = Input.mouseX
        #self.sprite2.rotation -= 2
        
        if Input.getKey("w"):
            self.sprite1.y -= 1
        if Input.getKey("s"):
            self.sprite1.y += 1
        if Input.getKey("a"):
            self.sprite1.x -= 1
        if Input.getKey("d"):
            self.sprite1.x += 1
        
        self.sprite2.currentFrame = random.randint(0, self.sprite2.maxFrames - 1)

        # Collision test
#        if self.sprite1.hitTestPoint(Input.mouseX, Input.mouseY): #self.sprite2):
#            print("Collision detected!")
#        else:
#            print("No collision.")


if __name__ == "__main__":
    game = MyGame()
    game.run()