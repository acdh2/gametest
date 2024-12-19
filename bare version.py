import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import math
import random
import glfw

class Game():
    """
    Base Game class that handles the window, main loop, and rendering.
    Extends GameObject so Sprites can be added directly to it.
    """
    def __init__(self, width=800, height=600, title="Game"):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.window = None

    def setupWindow(self):
        """Initialize GLFW and create a window."""
        if not glfw.init():
            raise Exception("GLFW initialization failed!")

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window creation failed!")

        glfw.make_context_current(self.window)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)

    def run(self):
        """Main loop of the game."""
        self.setupWindow()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            #draw "hello world" here

            glfw.swap_buffers(self.window)

        glfw.terminate()

if __name__ == "__main__":
    game = Game()
    game.run()