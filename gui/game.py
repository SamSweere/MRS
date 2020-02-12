"""
Platformer Game
"""
import arcade
import math
from simulation.World import World

# Constants
SCREEN_TITLE = "Platformer"

class MyGame(arcade.Window):
    """
    Main application class.
    Should render output and handle user input.
    """

    def __init__(self, env_width, env_height, walls, robot):
        self.env_width = env_width
        self.env_height = env_height
        self.SCREEN_WIDTH = env_width
        self.SCREEN_HEIGHT = env_height
        self.walls = walls
        self.robot = robot

        # Call the parent class and set up the window
        super().__init__(self.env_width, self.env_height, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.setup()

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        self.world = World(self.walls, self.robot)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        
        for wall in self.world.walls:
            arcade.draw_polygon_filled(wall.points, color=arcade.csscolor.BLACK)
            
        self.__draw_robot__()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call the updates of all the moving parts
        self.robot.update()
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        # Forward/back
        if key == arcade.key.UP:
            self.robot.speed = 1
        elif key == arcade.key.DOWN:
            self.robot.speed = -1

        # Rotate left/right
        elif key == arcade.key.LEFT:
            self.robot.change_angle = 1
        elif key == arcade.key.RIGHT:
            self.robot.change_angle = -1

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.robot.speed = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.robot.change_angle = 0

    def __draw_robot__(self):       
        # Draw the shape of the robot as an circle with an line marking its rotation
        old_x = self.robot.radius
        old_y = 0

        angle_rad = math.radians(self.robot.angle)

        rotated_x = self.robot.x + math.cos(angle_rad) * old_x - math.sin(angle_rad) * old_y
        rotated_y = self.robot.y + math.sin(angle_rad) * old_x + math.cos(angle_rad) * old_y
        
        arcade.draw_circle_outline(self.robot.x, self.robot.y, self.robot.radius, color=arcade.csscolor.BLACK)
        arcade.draw_line(self.robot.x, self.robot.y, rotated_x, rotated_y, color=arcade.csscolor.BLACK)
        
        
            