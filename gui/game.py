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
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        # Just for debugging, rotate the agent to check our drawing function
        if key == arcade.key.UP:
            self.world.robot.angle += math.pi / 10
            
    def __draw_robot__(self):
        rob = self.world.robot
        
        # Draw the shape of the robot as an circle with an line marking its rotation
        old_x = rob.radius
        old_y = 0
        rotated_x = rob.x + math.cos(rob.angle) * old_x - math.sin(rob.angle) * old_y
        rotated_y = rob.y + math.sin(rob.angle) * old_x + math.cos(rob.angle) * old_y
        
        arcade.draw_circle_outline(rob.x, rob.y, rob.radius, color=arcade.csscolor.BLACK)
        arcade.draw_line(rob.x, rob.y, rotated_x, rotated_y, color=arcade.csscolor.BLACK)
        
        
            