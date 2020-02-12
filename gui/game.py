"""
Platformer Game
"""
import arcade
from simulation.World import World, create_rect_wall
from simulation.Robot import Robot

# Constants
SCREEN_TITLE = "Platformer"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, environment_width, environment_height):
        self.SCREEN_WIDTH = environment_width
        self.SCREEN_HEIGHT = environment_height

        # Call the parent class and set up the window
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        walls = [
            create_rect_wall(self.SCREEN_WIDTH/2 - 200 , self.SCREEN_HEIGHT/2 - 200, 100, 50)
        ]
        robot = Robot(self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2)
        self.world = World(walls, robot)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        
        for wall in self.world.walls:
            arcade.draw_polygon_filled(wall.points, color=arcade.csscolor.BLACK)
            
        self.__draw_robot__()
            
    def __draw_robot__(self):
        rob = self.world.robot
        arcade.draw_circle_outline(rob.x, rob.y, rob.radius, color=arcade.csscolor.BLACK)
            