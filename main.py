from game import *
from level import *
from player import *

class MyGame(Game):
    def __init__(self):
        super().__init__(width=640, height=480, title="Game")

    def setup(self):                
        self.level = Level(self.collisionManager)
        self.level.setup()
        self.addChild(self.level)
        
        self.text = Text("Hello world", x=0, y=0, rotation=0, scaleX=1, scaleY=1, originX=0, originY=0)
        self.addChild(self.text)    
        
        sound = Sound("assets/snowland.ogg")
        sound.play()            
        
    def update(self):
        """Update and test for collisions."""        
        self.level.update()

if __name__ == "__main__":
    game = MyGame()
    game.run()