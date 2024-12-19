import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import math
import random
import sounddevice as sd
import soundfile as sf
import threading

#set up bitmap font
fontName, fontColumns, fontRows = "assets/font.png", 18, 6

#---------------------------------------------------------------------------------------------------------------------
#                                                           transform_point()
#---------------------------------------------------------------------------------------------------------------------
# Helper: Transform point by rotation, scale, and translation
def transform_point(x, y, tx, ty, rotation, scaleX, scaleY):
    # Convert rotation to radians
    angle_rad = math.radians(rotation)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Apply scale, then rotation, then translation
    x_scaled, y_scaled = x * scaleX, y * scaleY
    x_rot = x_scaled * cos_a - y_scaled * sin_a
    y_rot = x_scaled * sin_a + y_scaled * cos_a
    return x_rot + tx, y_rot + ty

#---------------------------------------------------------------------------------------------------------------------
#                                                      *** class Sound ***
#---------------------------------------------------------------------------------------------------------------------
class Sound:
    """
    A class to handle loading, playing, and stopping sounds using sounddevice and soundfile.
    """
    def __init__(self, filepath):
        """
        Load an audio file.
        :param filepath: Path to the audio file (e.g., OGG, WAV).
        """
        self.filepath = filepath
        self.data, self.samplerate = sf.read(filepath, dtype='float32')
        self._is_playing = False
        self._lock = threading.Lock()

#---------------------------------------------------------------------------------------------------------------------
#                                                           play()
#---------------------------------------------------------------------------------------------------------------------
    def play(self):
        """
        Play the loaded audio file.
        """
        with self._lock:
            if self._is_playing:
                self.stop()  # Ensure no overlapping playback

            self._is_playing = True
            threading.Thread(target=self._play_thread, daemon=True).start()

#---------------------------------------------------------------------------------------------------------------------
#                                                        _play_thread()
#---------------------------------------------------------------------------------------------------------------------
    def _play_thread(self):
        """
        Internal method to handle playback in a separate thread.
        """
        try:
            sd.play(self.data, samplerate=self.samplerate)
            sd.wait()  # Wait until playback finishes
        finally:
            with self._lock:
                self._is_playing = False

#---------------------------------------------------------------------------------------------------------------------
#                                                           stop()
#---------------------------------------------------------------------------------------------------------------------
    def stop(self):
        """
        Stop the currently playing sound.
        """
        with self._lock:
            if self._is_playing:
                sd.stop()
                self._is_playing = False

#---------------------------------------------------------------------------------------------------------------------
#                                                           is_playing()
#---------------------------------------------------------------------------------------------------------------------
    def is_playing(self):
        """
        Check if the sound is currently playing.
        :return: Boolean indicating playback status.
        """
        with self._lock:
            return self._is_playing

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class Input:
    """Singleton class to handle keyboard and mouse input."""
    _instance = None
    _current_keys = set()
    _previous_keys = set()
    mouseX = 0
    mouseY = 0

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Input, cls).__new__(cls)
        return cls._instance

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @classmethod
    def update(cls, window):
        """
        Update the current key states and mouse position.
        Should be called once per frame.
        """
        # Update mouse position
        cls.mouseX, cls.mouseY = glfw.get_cursor_pos(window)

        # Swap key states
        cls._previous_keys = cls._current_keys.copy()
        cls._current_keys.clear()

        # Check which keys are pressed this frame
        for key in range(glfw.KEY_SPACE, glfw.KEY_LAST):
            if glfw.get_key(window, key) == glfw.PRESS:
                cls._current_keys.add(key)

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @classmethod
    def getKey(cls, key_name):
        """Return True if the specified key is being held down."""
        key = cls._key_to_glfw_key(key_name)
        return key in cls._current_keys

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @classmethod
    def getKeyDown(cls, key_name):
        """Return True if the specified key was pressed this frame."""
        key = cls._key_to_glfw_key(key_name)
        return key in cls._current_keys and key not in cls._previous_keys

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @classmethod
    def getKeyUp(cls, key_name):
        """Return True if the specified key was released this frame."""
        key = cls._key_to_glfw_key(key_name)
        return key not in cls._current_keys and key in cls._previous_keys

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _key_to_glfw_key(key_name):
        """
        Convert a string key name to a GLFW key constant.
        For example: "w" -> glfw.KEY_W
        """
        if len(key_name) == 1 and key_name.isalpha():
            return getattr(glfw, f"KEY_{key_name.upper()}")
        elif key_name == "space":
            return glfw.KEY_SPACE
        else:
            raise ValueError(f"Unknown key name: {key_name}")

# Texture cache to store loaded textures
_texture_cache = {}

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class Texture:
    """Class to hold texture data: OpenGL ID, width, and height."""
    def __init__(self, texture_id, width, height):
        self.texture_id = texture_id
        self.width = width
        self.height = height

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
def loadTexture(filename):
    """
    Load a texture from a file.
    If the texture has already been loaded, return the cached version.
    """
    global _texture_cache

    # Return cached texture if it exists
    if filename in _texture_cache:
        return _texture_cache[filename]

    # Load texture image
    image = Image.open(filename).convert("RGBA")  # Ensure RGBA format
    img_data = np.array(image)

    # Generate OpenGL texture ID
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Upload texture data to OpenGL
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    # Create a Texture object and cache it
    texture = Texture(tex_id, image.width, image.height)
    _texture_cache[filename] = texture

    return texture

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class GameObject:
    """
    Base class for all game objects.
    Handles position, rotation, scale, matrix transformations, and parent-child relationships.
    """
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __init__(self, x=0, y=0, rotation=0, scaleX=1, scaleY=1):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.children = []  # List to store child GameObjects
        self.parent = None  # Reference to the parent GameObject

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def addChild(self, child):
        """Add a child GameObject to this GameObject."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def render(self):
        """Render this GameObject and its children."""
        glPushMatrix()

        # Apply transformations
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        glScalef(self.scaleX, self.scaleY, 1)

        # Draw self
        self.draw()

        # Render children
        for child in self.children:
            child.render()

        glPopMatrix()

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def draw(self):
        """To be implemented by subclasses."""
        pass
        
    def hitTest(self, other):
        """Default hitTest method. Always returns False."""
        return False

    def hitTestPoint(self, x, y):
        """Default hitTestPoint method. Always returns False."""
        return False

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class Sprite(GameObject):
    """
    Sprite class that draws a textured quad.
    """
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __init__(self, texture_path, x=0, y=0, rotation=0, scaleX=1, scaleY=1, originX=None, originY=None):
        super().__init__(x, y, rotation, scaleX, scaleY)

        self.texture = loadTexture(texture_path)
        self.width = self.texture.width
        self.height = self.texture.height
        
        # Origin point (pivot for transformations)
        self.originX = originX if originX is not None else self.width // 2
        self.originY = originY if originY is not None else self.height // 2
        
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def draw(self):
        """Draw the textured quad."""
        glTranslatef(-self.originX, -self.originY, 0)
        glBindTexture(GL_TEXTURE_2D, self.texture.texture_id)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.texture.width, 0)
        glTexCoord2f(1, 1); glVertex2f(self.texture.width, self.texture.height)
        glTexCoord2f(0, 1); glVertex2f(0, self.texture.height)
        glEnd()
        
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def getCorners(self):
        """
        Calculate the 4 corners of the sprite in world space.
        Returns a list of (x, y) tuples.
        """
        hw = self.width / 2
        hh = self.height / 2

        # Local corners relative to the origin
        local_corners = [
            (-self.originX, -self.originY),           # Top-left
            (self.width - self.originX, -self.originY),    # Top-right
            (self.width - self.originX, self.height - self.originY),  # Bottom-right
            (-self.originX, self.height - self.originY)   # Bottom-left
        ]

        # Transform corners to world space
        world_corners = [transform_point(x, y, self.x, self.y, self.rotation, self.scaleX, self.scaleY)
                         for x, y in local_corners]
        return world_corners        

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def hitTest(self, other):
        """
        Test for collision with another Sprite using OBB collision detection.
        Returns True if colliding, False otherwise.
        """
        if not isinstance(other, Sprite):
            return False

        # Get corners for both sprites
        corners1 = self.getCorners()
        corners2 = other.getCorners()

        # Get axes for SAT (Separating Axis Theorem)
        axes = self._getAxes(corners1) + self._getAxes(corners2)

        # Check for overlap on all axes
        for axis in axes:
            if not self._overlap_on_axis(axis, corners1, corners2):
                return False  # Separating axis found, no collision
        return True  # No separating axis, collision detected
        
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def hitTestPoint(self, x, y):
        """
        Check if a point (x, y) in screen space intersects this Sprite.
        Considers the Sprite's position, rotation, and scale.
        """
        # Step 1: Translate point to local space
        # Undo the transformations: Translate -> Rotate -> Scale (in reverse order)

        # Move the point relative to the sprite's position
        localX = x - self.x
        localY = y - self.y

        # Undo rotation
        angle_rad = -math.radians(self.rotation)  # Negative because we reverse rotation
        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)

        rotatedX = localX * cos_theta - localY * sin_theta
        rotatedY = localX * sin_theta + localY * cos_theta

        # Undo scaling
        if self.scaleX != 0:
            rotatedX /= self.scaleX
        if self.scaleY != 0:
            rotatedY /= self.scaleY

        # Step 2: Account for origin offset and check bounds
        # The sprite's rectangle is defined by the top-left (0, 0) to (width, height)
        rectLeft = -self.originX
        rectRight = rectLeft + self.texture.width
        rectTop = -self.originY
        rectBottom = rectTop + self.texture.height

        # Check if the transformed point is within the bounds of the rectangle
        if rectLeft <= rotatedX <= rectRight and rectTop <= rotatedY <= rectBottom:
            return True
        return False

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def _getAxes(self, corners):
        """Get the axes to test for SAT based on edges of the rectangle."""
        axes = []
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]  # Next corner
            edge = (p2[0] - p1[0], p2[1] - p1[1])  # Edge vector
            normal = (-edge[1], edge[0])  # Perpendicular vector
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            axes.append((normal[0] / length, normal[1] / length))  # Normalize
        return axes

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def _overlap_on_axis(self, axis, corners1, corners2):
        """Check for overlap between two rectangles on a given axis."""
        def project(corners, axis):
            return [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners]

        projection1 = project(corners1, axis)
        projection2 = project(corners2, axis)

        # Find min and max projections
        min1, max1 = min(projection1), max(projection1)
        min2, max2 = min(projection2), max(projection2)

        # Check for overlap
        return not (max1 < min2 or max2 < min1)

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class AnimSprite(Sprite):
    """A Sprite class for rendering a sliced (animated) texture."""
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __init__(self, texture_path, columns=1, rows=1, x=0, y=0, rotation=0, scaleX=1, scaleY=1, originX=None, originY=None):
        super().__init__(texture_path, x, y, rotation, scaleX, scaleY, originX, originY)
        self.columns = columns  # Number of columns in the sliced texture
        self.rows = rows  # Number of rows in the sliced texture
        self.currentFrame = 0  # Current frame of the animation

        # Ensure that the texture can be sliced properly
        self.frameWidth = self.texture.width // self.columns
        self.frameHeight = self.texture.height // self.rows
        
        self.width = self.frameWidth#texture.width
        self.height = self.frameHeight#texture.height        

        self.maxFrames = self.columns * self.rows  # Maximum number of frames

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def draw(self):
        """Override the draw method to render a specific frame of the sliced texture."""
        if 0 <= self.currentFrame < self.maxFrames:
            # Calculate the column and row for the current frame
            col = self.currentFrame % self.columns
            row = self.currentFrame // self.columns

            # Calculate texture coordinates (normalized 0 to 1)
            left = col * self.frameWidth / self.texture.width
            right = (col + 1) * self.frameWidth / self.texture.width
            top = ((row + 1) * self.frameHeight / self.texture.height)
            bottom = (row * self.frameHeight / self.texture.height)

            # Adjust for the origin offset
            glTranslatef(-self.originX, -self.originY, 0)
            glBindTexture(GL_TEXTURE_2D, self.texture.texture_id)

            # Render the textured quad using the calculated texture coordinates
            glBegin(GL_QUADS)
            glTexCoord2f(left, bottom)
            glVertex2f(0, 0)  # Top-left

            glTexCoord2f(right, bottom)
            glVertex2f(self.frameWidth, 0)  # Top-right

            glTexCoord2f(right, top)
            glVertex2f(self.frameWidth, self.frameHeight)  # Bottom-right

            glTexCoord2f(left, top)
            glVertex2f(0, self.frameHeight)  # Bottom-left
            glEnd()
            
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class Text(AnimSprite):
    """
    A class to render text using a sliced font image.
    """
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __init__(self, text="", x=0, y=0, rotation=0, scaleX=1, scaleY=1, originX=None, originY=None):    
        super().__init__(fontName, fontColumns, fontRows, x, y, rotation, scaleX, scaleY, originX, originY)
        self.value = text    # Text to render
        self.charWidth = self.texture.width / 18
        self.charHeight = self.texture.height / 6
        self.width = self.charWidth * len(text)
        self.height = self.charHeight
        self.originX = originX if originX is not None else self.width // 2
        self.originY = originY if originY is not None else self.height // 2

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @property
    def text(self):
        return self.value

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    @text.setter
    def text(self, charID):
        self.width = self.charWidth * len(new_text)
        self.value = new_text

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def drawCharacter(self, charID):
        """Override the draw method to render a specific frame of the sliced texture."""
        if 0 <= charID < self.maxFrames:
            # Calculate the column and row for the current frame
            col = charID % self.columns
            row = charID // self.columns

            # Calculate texture coordinates (normalized 0 to 1)
            left = col * self.frameWidth / self.texture.width
            right = (col + 1) * self.frameWidth / self.texture.width
            top = ((row + 1) * self.frameHeight / self.texture.height)
            bottom = (row * self.frameHeight / self.texture.height)

            # Render the textured quad using the calculated texture coordinates
            glBegin(GL_QUADS)
            glTexCoord2f(left, bottom)
            glVertex2f(0, 0)  # Top-left

            glTexCoord2f(right, bottom)
            glVertex2f(self.frameWidth, 0)  # Top-right

            glTexCoord2f(right, top)
            glVertex2f(self.frameWidth, self.frameHeight)  # Bottom-right

            glTexCoord2f(left, top)
            glVertex2f(0, self.frameHeight)  # Bottom-left
            glEnd()
            
            glTranslatef(14, 0, 0)
            
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def draw(self):
        # Adjust for the origin offset
        glTranslatef(-self.originX, -self.originY, 0)
        glBindTexture(GL_TEXTURE_2D, self.texture.texture_id)
                
        for char in self.value:
            # Map character to its ASCII value
            ascii_value = ord(char)
            if 32 <= ascii_value <= 126:
                char_index = ascii_value - 32
                self.drawCharacter(char_index)

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
class Game(GameObject):
    """
    Base Game class that handles the window, main loop, and rendering.
    Extends GameObject so Sprites can be added directly to it.
    """
#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def __init__(self, width=800, height=600, title="Game"):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.window = None

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
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
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def setup(self):
        """To be overridden by subclasses."""
        pass

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def update(self):
        """To be overridden by subclasses."""
        pass

#---------------------------------------------------------------------------------------------------------------------
#                                                           
#---------------------------------------------------------------------------------------------------------------------
    def run(self):
        """Main loop of the game."""
        self.setupWindow()
        self.setup()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            Input.update(self.window)
            self.update()
            self.render()

            glfw.swap_buffers(self.window)

        glfw.terminate()
